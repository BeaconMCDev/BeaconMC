from vector import Vector

class Location:
    def __init__(self, x, y, z, pitch, yaw):
        self.x, self.y, self.z, self.yaw, self.pitch = x, y, z, yaw, pitch
        
    def move(self, vector:Vector):
        assert isinstance(vector, Vector)
        self.x += vector.x
        self.y += vector.y
        self.z += vector.z
        
    def rotate(self, pitch, yaw):
        self.pitch, self.yaw = pitch, yaw