
from PIL import Image

def generate_qr_code(data, filename):
    import qrcode
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=5,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)

def add_logo_to_qr(qr_img_path, logo_path, output_path):
    qr_img = Image.open(qr_img_path)
    logo = Image.open(logo_path)

    # Ensure the logo has an alpha channel
    if logo.mode != 'RGBA':
        logo = logo.convert("RGBA")

    # Calculate the size and position of the logo
    qr_width, qr_height = qr_img.size
    logo_size = int(qr_width * 0.25)  # Logo size as 25% of the QR code size
    logo.thumbnail((logo_size, logo_size), Image.ANTIALIAS)

    # Calculate position: centered
    logo_width, logo_height = logo.size
    position = ((qr_width - logo_width) // 2, (qr_height - logo_height) // 2)

    # Paste the logo into the QR code, using the logo itself as the transparency mask
    qr_img.paste(logo, position, mask=logo)

    # Save the result
    qr_img.save(output_path)

