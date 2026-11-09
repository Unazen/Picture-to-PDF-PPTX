# Превращает картинки в PDF или PPTX (одна картинка = один слайд/страница на весь экран).

## Примеры:
   ``` python photos_to_doc.py                                  # картинки из текущей папки -> <папка>.pptx
    python photos_to_doc.py ~/Pictures/trip                  # папка -> trip.pptx в текущей папке
    python photos_to_doc.py ~/Pictures/trip -s                       # сохранить рядом с фото
    python photos_to_doc.py ~/Pictures/trip -s -o deck.pptx          # своё имя, но рядом с фото
    python photos_to_doc.py ~/Pictures/trip -o ~/out/trip.pdf        # формат по расширению
    python photos_to_doc.py ~/Pictures/trip -t pdf                   # формат явно
    python photos_to_doc.py a.png b.png c.jpg -o slides.pptx         # список файлов
    python photos_to_doc.py ./shots -e png jpg -o deck.pptx          # только png и jpg
    python photos_to_doc.py ./shots -r                               # включая подпапки
```
## Зависимости: 

```
pip install pillow python-pptx
```
