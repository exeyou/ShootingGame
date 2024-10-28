import logging
from settings import win_width, win_height
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CollisionHandler:
    @staticmethod
    def check_collision(movable, blocks):
        for block in blocks:
            if movable.rect.colliderect(block.rect):
                logging.info("Зіткнення з блоком на позиції %s", block.rect.topleft)
                CollisionHandler.resolve_collision(movable, block)
        if movable.rect.left < 0:
            movable.rect.left = 0
        if movable.rect.right > win_width:
            movable.rect.right = win_width
        if movable.rect.top < 0:
            movable.rect.top = 0
        if movable.rect.bottom > win_height:
            movable.rect.bottom = win_height

    @staticmethod
    def resolve_collision(movable, block):
        if movable.rect.right > block.rect.left and movable.rect.left < block.rect.left:
            movable.rect.right = block.rect.left
        elif movable.rect.left < block.rect.right and movable.rect.right > block.rect.right:
            movable.rect.left = block.rect.right
        elif movable.rect.bottom > block.rect.top and movable.rect.top < block.rect.top:
            movable.rect.bottom = block.rect.top
        elif movable.rect.top < block.rect.bottom and movable.rect.bottom > block.rect.bottom:
            movable.rect.top = block.rect.bottom
