from PIL import Image
img = Image.open("Testing/forest.jpg")
img = img.resize((img.width * 4, img.height * 4), Image.NEAREST)
img.save("forest_resized.jpg")