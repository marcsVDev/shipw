from pygame import Rect, Surface
class AnimatedSprite():
    def __init__(self, spritesheet: Surface, frame_time: float, size: int):
        self.spritesheet = spritesheet
        self.frame_time = frame_time
        self.time = 0
        self.current_rect = Rect(0, 0, size, size)
        self.frame = 0
        self.size = size

    def update_frame(self, delta):
        self.time += delta  
        if self.time > self.frame_time:            
            if self.frame >= self.spritesheet.get_width() / self.size:
                self.frame = 0

            self.current_rect = Rect(self.frame * self.size, 0, self.size, self.size)
            self.frame += 1
            self.time = 0        

    def get_current_frame(self) -> Surface:
        return self.spritesheet.subsurface(self.current_rect)