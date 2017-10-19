from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import io
import operator
#import util as u
import logging
log = logging.getLogger()



def rectangle(draw, coords, fill, width = 1):
    '''
    expects a list [x0,y0, x1,y1]
    just because PIL draw.rectangle() does not support pixelwidth > 1
    '''
    x0,y0,x1,y1 = coords
    draw.line([x0,y0, x1, y0], fill, width)
    draw.line([x1,y0, x1, y1], fill, width)
    draw.line([x1,y1, x0, y1], fill, width)
    draw.line([x0,y1, x0, y0], fill, width)

    return draw


def paint_boxes(img, faces):
    '''
    takes a jpeg image and face json in Azure face API format
    returns an image with painted boxes and added captions
    '''
    if faces == []:
        log.info("No faces. returning original image")
        return img

    im = Image.open(io.BytesIO(img))
    draw = ImageDraw.Draw(im)
    width, height = im.size
    log.debug("Image width: {} height {}".format(width,height))
    
    ret = io.BytesIO()
    
    for f in faces:
        
        log.debug("Operating on face entry:\n {}".format(f))
        
        rect = f['faceRectangle']

        coords = [rect['left'], rect['top'], rect['left'] + rect['width'], 
                    rect['top']+rect['height']]
        #draw.rectangle(rect, outline="red")
        rectangle(draw, coords, "red", 3)

        age = f['faceAttributes']['age']
        gender = f['faceAttributes']['gender']
        #getting the prevalent emotion
        emo_dict = f['faceAttributes']['emotion']
        emotion = max(emo_dict, key = emo_dict.get )
        #forming caption
        caption_topup = "Age: {}".format(age)
        caption_topbot = gender
        caption_bot = emotion
        
        font = ImageFont.truetype("img/arial.ttf", size=10)

        draw.text([coords[0],coords[1]-11], caption_topup, font = font, fill = "blue")

        draw.text([coords[0]+4,coords[1]+2], caption_topbot, font = font, fill = "blue")
        draw.text([coords[0]+4,coords[3]-11], caption_bot, font = font, fill = "blue")

        im.save(ret, "JPEG")
    return ret.getvalue()


def resize_img(img, newsize, fill_color = "black"):
    im = Image.open(io.BytesIO(img))
    #x,y = im.size
    im.thumbnail(newsize)
    ret = io.BytesIO()
    im.save(ret,"JPEG")
    return ret.getvalue()


if __name__ == '__main__':
    import sys, json
    #log.setLevel(logging.getLevelName(u.get_setting("app","log_level")))
    log.setLevel(logging.ERROR)
    log.addHandler(logging.StreamHandler(stream = sys.stdout))

    with open("img/multiple-faces.jpg","rb") as i:
        img = i.read()

    with open("img/test_json.json","r") as f:
        faces = json.load(f)
    #log.debug(str(faces))
    im = paint_boxes(img, faces)
    im = resize_img(im, (200,500))
    im = Image.open(io.BytesIO(im))
    im.show()

    
