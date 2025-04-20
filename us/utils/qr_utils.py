import qrcode
import io
import base64
from PIL import Image

def generate_qr_code(text, width=250, height=250, gradient1="#4285f4", gradient2="#1a73e8"):
    """
    Generate a QR code for the given text.
    
    Args:
        text (str): The text to encode in the QR code
        width (int): Width of the QR code in pixels
        height (int): Height of the QR code in pixels
        gradient1 (str): Not used in current implementation
        gradient2 (str): Not used in current implementation
    
    Returns:
        str: Base64 encoded image data URI for the QR code
    """
    # Create QR code instance with appropriate settings for maximum readability
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    
    # Add data to the QR code
    qr.add_data(text)
    qr.make(fit=True)
    
    # Create a standard black and white QR code for maximum compatibility
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    # Resize to desired dimensions
    qr_img = qr_img.resize((width, height))
    
    # Save the image to a BytesIO object
    buffered = io.BytesIO()
    qr_img.save(buffered, format="PNG")
    
    # Get the base64-encoded image
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    # Return data URI
    return f"data:image/png;base64,{img_str}" 