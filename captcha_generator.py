from PIL import Image, ImageDraw, ImageFont
import random
import string
import io
import base64

class CaptchaGenerator:
    def __init__(self, width=200, height=80):
        self.width = width
        self.height = height
        self.font_size = 36
        
    def generate_code(self, length=5):
        chars = string.ascii_uppercase + string.digits
        chars = chars.replace('0', '').replace('O', '').replace('I', '').replace('1')
        return ''.join(random.choice(chars) for _ in range(length))
    
    def create_image(self, code):
        img = Image.new('RGB', (self.width, self.height), color='white')
        draw = ImageDraw.Draw(img)
        
        self._add_noise(draw)
        
        self._draw_text(draw, code)
        
        self._add_lines(draw)
        
        return img
    
    def _add_noise(self, draw):
        for _ in range(100):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            draw.point((x, y), fill=color)
    
    def _draw_text(self, draw, code):
        try:
            font = ImageFont.truetype("arial.ttf", self.font_size)
        except:
            font = ImageFont.load_default()
        
        text_width = draw.textlength(code, font=font)
        start_x = (self.width - text_width) // 2
        start_y = (self.height - self.font_size) // 2
        
        x_offset = 0
        for char in code:
            char_width = draw.textlength(char, font=font)
            
            char_x = start_x + x_offset + random.randint(-5, 5)
            char_y = start_y + random.randint(-10, 10)
            
            color = (
                random.randint(0, 100),
                random.randint(0, 100), 
                random.randint(0, 100)
            )
            
            draw.text((char_x, char_y), char, fill=color, font=font)
            x_offset += char_width + 5
    
    def _add_lines(self, draw):
        for _ in range(5):
            start = (random.randint(0, self.width), random.randint(0, self.height))
            end = (random.randint(0, self.width), random.randint(0, self.height))
            color = (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200))
            draw.line([start, end], fill=color, width=2)
    
    def generate_captcha(self):
        code = self.generate_code()
        image = self.create_image(code)
        
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        image_data = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            'code': code,
            'image_data': f"data:image/png;base64,{image_data}",
            'image': image
        }

def create_captcha_session(session):
    generator = CaptchaGenerator()
    captcha = generator.generate_captcha()
    
    session['captcha_code'] = captcha['code']
    
    return captcha['image_data']

def validate_captcha_session(session, user_input):
    if 'captcha_code' not in session:
        return False
    
    stored_code = session.get('captcha_code', '').upper()
    user_code = user_input.upper().strip()
    
    session.pop('captcha_code', None)
    
    return stored_code == user_code

if __name__ == "__main__":
    generator = CaptchaGenerator()
    captcha = generator.generate_captcha()
    
    print(f"Código generado: {captcha['code']}")
    print(f"Imagen guardada como: captcha_test.png")
    
    captcha['image'].save('captcha_test.png')