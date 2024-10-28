from enemies import Zombie, Shooter

class EnemyFactory:
    @staticmethod
    def create_enemy(enemy_type, x, y):
        if enemy_type == "zombie":
            return Zombie(x, y)
        elif enemy_type == "shooter":
            return Shooter(x, y)
