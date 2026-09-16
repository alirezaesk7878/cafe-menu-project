import qrcode

menu_url = "http://192.168.75.231:5500/front-end/index.html"

img = qrcode.make(menu_url)
img.save("menu_qr.png")
print("QR Code ساخته شد: menu_qr.png")