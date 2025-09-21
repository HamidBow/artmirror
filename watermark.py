import os
from PIL import Image, ImageDraw, ImageFont

# ---- CONFIGURATION DU FILIGRANE ----
# Le texte du filigrane
WATERMARK_TEXT = "Hamid Art Mirror"
# Chemin du dossier contenant les images à traiter
IMAGES_FOLDER = os.path.expanduser("~/Bureau/test_watermark")
# Chemin du dossier de sortie où les images filigranées seront sauvegardées
OUTPUT_FOLDER = os.path.expanduser("~/Bureau/test_watermark_output")

# Paramètres du filigrane
FONT_SIZE_RATIO = 0.05  # Taille de la police par rapport à la largeur de l'image (5%)
OPACITY = 150            # Transparence du filigrane (0-255, 50 est semi-transparent)
ROTATION_ANGLE = 25     # Angle d'inclinaison du filigrane en degrés

# ---- FONCTION POUR CRÉER LE FILIGRANE ----
def create_watermark(image_path, output_path):
    try:
        # Ouvrir l'image originale
        base_image = Image.open(image_path).convert("RGBA")
        
        # Créer une couche transparente pour le filigrane
        watermark_layer = Image.new("RGBA", base_image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(watermark_layer)

        # Calculer la taille de la police en fonction de la taille de l'image
        width, height = base_image.size
        font_size = int(width * FONT_SIZE_RATIO)
        
        try:
            # Essayer d'utiliser une police professionnelle si elle existe
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
        except IOError:
            # Sinon, utiliser la police par défaut de Pillow
            font = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", font_size)

        # Utilisation de textbbox() à la place de textsize() (pour les versions de Pillow > 9.1.0)
        left, top, right, bottom = draw.textbbox((0, 0), WATERMARK_TEXT, font=font)
        text_width = right - left
        text_height = bottom - top
        
        # Placer le texte de manière répétée et oblique
        for y in range(-height, height, int(text_height * 2.5)):
            for x in range(-width, width, int(text_width * 1.5)):
                # Créer une image de texte et la faire pivoter
                text_image = Image.new("RGBA", (text_width, text_height), (255, 255, 255, 0))
                text_draw = ImageDraw.Draw(text_image)
                text_draw.text((0, 0), WATERMARK_TEXT, font=font, fill=(255, 255, 255, OPACITY))
                
                rotated_text = text_image.rotate(ROTATION_ANGLE, expand=1, resample=Image.BICUBIC)
                
                # Placer le texte pivoté sur la couche du filigrane
                watermark_layer.paste(rotated_text, (x, y), rotated_text)
                
        # Fusionner le filigrane avec l'image de base
        final_image = Image.alpha_composite(base_image, watermark_layer)

        # CORRECTION : Convertir l'image en RGB avant de la sauvegarder en JPEG
        rgb_image = final_image.convert('RGB')
        rgb_image.save(output_path, "JPEG", quality=95)
        print(f"✅ Filigrane appliqué à {os.path.basename(image_path)}")

    except Exception as e:
        print(f"❌ Erreur lors du traitement de {os.path.basename(image_path)} : {e}")

# ---- TRAITEMENT EN LOT ----
if __name__ == "__main__":
    # Créer le dossier de sortie s'il n'existe pas
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    # Parcourir toutes les images du dossier
    for filename in os.listdir(IMAGES_FOLDER):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(IMAGES_FOLDER, filename)
            output_path = os.path.join(OUTPUT_FOLDER, filename)
            
            # Appliquer le filigrane
            create_watermark(image_path, output_path)

    print("--- Processus terminé ---")
