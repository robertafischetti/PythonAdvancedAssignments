"""---------------------------------------------------------------------------------------
 Module: cube

 Author = Roberta Fischetti

 Date = 2026-07-28

 Description = Cube class - assignment.
---------------------------------------------------------------------------------------"""

"""
CUBE CLASS

1. CREATE an abstract class "Cube" with the functions:
   translate(x, y, z), rotate(x, y, z), scale(x, y, z) and color(R, G, B)
   All functions store and print out the data in the cube (translate, rotate, scale and color).

2. ADD an __init__(name) and create 3 cube objects.

3. ADD the function print_status() which prints all the variables nicely formatted.

4. ADD the function update_transform(ttype, value).
   "ttype" can be "translate", "rotate" and "scale" while "value" is a list of 3 floats.
   This function should trigger either the translate, rotate or scale function.

   BONUS: Can you do it without using ifs?

5. CREATE a parent class "Object" which has a name, translate, rotate and scale.
   Use Object as the parent for your Cube class.
   Update the Cube class to not repeat the content of Object.

"""

# CLASS ----------------------------------------------------
class Object:
   def __init__(self, name):
         self.name = name
         self.translate = [0, 0, 0]
         self.rotate = [0, 0, 0]
         self.scale = [1, 1, 1]
      

class Cube(Object):
   def __init__(self, name):
      super().__init__(name)
      self.color = [255, 255, 255]

      print(f"Cube {self.name} initialized.")

   def translate_by(self, dx, dy, dz):
      self.translate[0] += dx 
      self.translate[1] += dy
      self.translate[2] += dz

      print(f"Cube {self.name} translated. Now at position {self.translate}.")

   def rotate_by(self, dx, dy, dz):
      self.rotate[0] += dx 
      self.rotate[1] += dy
      self.rotate[2] += dz   

      print(f"Cube {self.name} rotated. Now at position {self.rotate}.")

   def scale_by(self, dx, dy, dz):
      self.scale[0] *= dx 
      self.scale[1] *= dy
      self.scale[2] *= dz 
      
      print(f"Cube {self.name} rotated. Now at position {self.scale}.")

   def set_color(self, R, G, B):
      self.color = [R, G, B]

      print(f"Cube {self.name} rotated. Now at position {self.color}.")

   def print_status(self):
      print(f"{self.name} created with the following attributes:\n\
      - position: {self.translate}\n\
      - rotation {self.rotate}\n\
      - scale: {self.scale}\n\
      - color: {self.color}.")

   def update_transform(self, ttype, value):
      ttype_dict = {
         "translate" : self.translate_by, 
         "rotate" : self.rotate_by,
         "scale" : self.scale_by,
      }

      ttype_dict[ttype](*value)


# START ---------------------------------------------------------------
   
cube1, cube2, cube3 = Cube("cube1"), Cube("cube2"), Cube("cube3")
    