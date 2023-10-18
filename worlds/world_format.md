# Worlds format (in files)
Xc, Yc, Zc are the coordinates of a chunk (16x16x16 blocks)
B is a block's type
N is the NBT tags of a block(will be done later)
L is the world level

Name::::L=====Xc1;Yc1;Zc1|B>N;B>N;B>N;...;B>N<<|<<Xc2;Yc2;Zc2|B>N;B>N;B>N;...;B>N<<|<<Xc3;Yc3;Zc3|B>N;B>N;B>N;...;B>N...

# World format (in the running server)
[[{"x": Xc1, "y": Yc1, "z": Zc1}, (B, N), (B, N), (B, N), (B, N), (B, N)..., (B, N)], 
[{"x": Xc2, "y": Yc2, "z": Zc2}, (B, N), (B, N), (B, N), (B, N), (B, N)..., (B, N)], 
[{"x": Xc3, "y": Yc3, "z": Zc3}, (B, N), (B, N), (B, N), (B, N), (B, N)..., (B, N)], ...]
+ an attribute for level in the world class
+ an attribute for the name in the world class

# Blocks id
- 0: air
- 1: grass_block
- 2: dirt
- 3: stone

# NBT
NBT are actually str. But not used