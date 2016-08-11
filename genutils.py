#!/usr/local/bin/python
# -*- coding: utf-8 -*-

# iboss-2
# filename: odspy.py
# author: - Thomas Meschede
# 
# usage: file loads ods file and puts data into a python array
#
# modified:
#	- 2012 10 25 - Thomas Meschede

"""script loads an ods file into python arrays"""

import bpy
import bpy.props
from bpy.props import FloatVectorProperty
import sys
import os
from itertools import chain
import numpy as np
import mathutils
from math import cos, sin, pi, atan,sqrt
pi2=pi/2

V3D = mathutils.Vector

import time
import bpy
import blendplot

activescene = None

normalized = lambda x: x/np.sqrt(np.sum(x*x))

def copyobject(oldobjname):
    me=bpy.data.objects[oldobjname].data

    ob = bpy.data.objects.new(oldobjname+"_cp",me) # create a new object
    ob.data = me          # link the mesh data to the object
    scene = bpy.context.scene           # get the current scene
    scene.objects.link(ob)                      # link the object into the scene
    return ob

def genobject(objname,verts=[],faces=[],edges=[], mat=None):
    me = bpy.data.meshes.new(objname)  # create a new mesh
    me.from_pydata(verts,edges,faces)
    me.update()      # update the mesh with the new data
    
    # Assign material to mesh
    if me.materials:
        # assign to 1st material slot
        me.materials[0] = mat
    else:
        # no slots
        me.materials.append(mat)
    ob = bpy.data.objects.new(objname,me) # create a new object
    ob.data = me          # link the mesh data to the object
    scene = bpy.context.scene           # get the current scene
    scene.objects.link(ob)                      # link the object into the scene
    return ob

def gen3dlist(size,initializer=None):
    vm=[None]*size[0]
    for i in range(size[0]):
     vm[i]=[None]*size[1]
     for j in range(size[1]):
      vm[i][j]=[initializer]*size[2]
    return vm

def getactiveobj():
    return bpy.context.scene.objects.active

def selectsingleobj(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select=True
    bpy.context.scene.objects.active=obj

def joinobjects(objlist):
    obj=genobject("joined")
    selectobj(obj)
    for i in objlist: i.select=True
    bpy.ops.object.join()
    return obj

def rotverts(verts,euler):
    rot=Euler(euler).to_matrix()    
    newverts=[]
    for i in verts:
        tmp=[]
        for j in i: 
            tmp.append(rot*Vector(j))
        newverts.append(tmp)
    return newverts
   
def creategeometry(verts):
    faces=[]
    faceoffset=0
    for ver in verts:
        if len(ver)==4: 
            faces.append((faceoffset+0,faceoffset+1,faceoffset+2,faceoffset+3))
            faceoffset+=4
        elif len(ver)==3:
            faces.append((faceoffset+0,faceoffset+1,faceoffset+2)) 
            faceoffset+=3
    return list(chain.from_iterable(verts)),faces

def createquadverts(size=(1,1),pos=(0,0,0),rot=(0,0,0)):
    newverts=[(0,0,0),(size[0],0,0),(size[0],size[1],0),(0,size[1],0)]
    rot=Euler(rot).to_matrix()
    verts=[]
    for i in newverts:
        verts.append(rot*Vector(i)+Vector(pos))
    return [verts]

def createcylinder(r,b1,b2,res):
    verts=[]
    for i in range(res):
       a=i*2*pi/res
       x,y=r*sin(a),r*cos(a)
       a=(i+1)*2*pi/res
       x2,y2=r*sin(a),r*cos(a)
       verts.append([(x,y,b1),(x2,y2,b1),(x2,y2,b2),(x,y,b2)])    
    return verts

def createcone(r,h,res):
    verts=[]
    for i in range(res):
       a=i*2*pi/res
       x,y=r*sin(a),r*cos(a)
       a=(i+1)*2*pi/res
       x2,y2=r*sin(a),r*cos(a)
       verts.append([(0.0,0.0,0.0),(x,y,-h),(x2,y2,-h)])
    return verts

def genobjandremovedoubles(verts, mat):
    verts,faces=creategeometry(verts)
    block=genobject("block",verts,faces, mat=mat)
    
    selectsingleobj(block)
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles()#threshhold=0.01)
    bpy.ops.object.editmode_toggle()
    return block 


def arrow(pos, vec, width=0.1, mat=None):
    # Generate the tracking quaternion that will account for the rotation
    vec = -V3D(vec)    
    quat=vec.to_track_quat("Z","X")
    length=vec.length

    #generate arrow-obj
    r = width*0.5
    res = 8
    verts = createcylinder(r,0.0+3*r,length,res)
    verts.extend(createcone(r*2.5,-r*4,res))

    #print(np.array(verts))

    ar = genobjandremovedoubles(verts, mat)   
    
        #obj2=cpobj("pfeil.schaft")
    ar.location=pos
        #obj2.scale=(width,width,length-lengthdiv)
    ar.rotation_mode="QUATERNION"
    ar.rotation_quaternion=quat
    return ar
    
def axis3d(mat,size=1.0):
    width = 0.01
    a1 = arrow((1,0,0),(1.0,0.0,0.0),width, mat) 
    a2 = arrow((0,1,0),(0.0,1.0,0.0),width, mat)
    a3 = arrow((0,0,1),(0.0,0.0,1.0),width, mat)

    return a1,a2,a3

def preparescene():
    global activescene
    bpy.context.user_preferences.view.show_splash = False    
    activescene = bpy.data.scenes.new("blendplot")  
    bpy.data.scenes.remove(bpy.data.scenes['Scene']) 

def addcamera(pos):
    #setup render scene
    #layer1=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False)
    cam_loc = pos
    #bpy.ops.object.camera_add(view_align=False, enter_editmode=False, 
    #                          location=cam_loc,
    #                            rotation=cam_ori, 
    #                            layers=layer1)
    cam = bpy.data.cameras.new("defaultview")
    cam_ob = bpy.data.objects.new("Camera", cam)
    scene = bpy.context.scene           # get the current scene
    scene.objects.link(cam_ob)
    bpy.context.scene.camera=cam_ob
    cam_ob.location = cam_loc
    cam_ob.rotation_mode="QUATERNION"
    cam_ob.rotation_quaternion = V3D(cam_loc).to_track_quat("Z","Y")    

from bpy.app.handlers import persistent
@persistent
def do_render_opengl():
    activescene.render.resolution_x=1024
    activescene.render.resolution_y=1024
    activescene.render.resolution_percentage=100
    activescene.render.filepath = blendplot.tempfile

    newworld = bpy.data.worlds.new("blendplot")
    newworld.horizon_color=(1.0,1.0,1.0)
    activescene.world=newworld

    #activescene.color_mode = 'RGBA'
    activescene.render.alpha_mode="TRANSPARENT"
    
    
    for area in bpy.context.screen.areas: # iterate through areas in current screen
      #print(area.type)
      if area.type == 'VIEW_3D':
        for space in area.spaces: # iterate through spaces in current VIEW_3D area
            #print(space.type)
            if space.type == 'VIEW_3D': # check if space is a 3D view
               print("changing from ",space.viewport_shade)
               space.viewport_shade = 'MATERIAL' # set the viewport shading to rendered
               space.region_3d.view_perspective = 'CAMERA'
               
    bpy.context.scene.update()
    #py.ops.wm.redraw_timer(type='DRAW', iterations=1)
    
    #from time import sleep
    #sleep(0.05)
    
    bpy.ops.render.opengl(animation=False, write_still=True, view_context=True)
    #bpy.ops.render.opengl(animation=False, write_still=True, view_context=False)
    #bpy.ops.image.save_as(save_as_render=True, copy=True, 
    #                      filepath=blendplot.tempfile, relative_path=True,
    #                      show_multiview=False, use_multiview=False)
    if not blendplot.showblender: bpy.ops.wm.quit_blender()
    #animation (boolean, (optional)) – Animation, Render files from the animation range of this scene
    #write_still (boolean, (optional)) – Write Image, Save rendered the image to the output path (used only when animation is disabled)
    #view_context (boolean, (optional)) – View Context, Use the current 3D view for rendering, else use scene settings.

#return w,x,y,z
def getquatrot(u,v):
  k_cos_theta = np.dot(u,v);
  u2 = np.sum(u*u)
  v2 = np.sum(v*v)
  k = sqrt(u2 * v2);

  if (k_cos_theta / k == -1):
    #180 degree rotation around any orthogonal vector
    x,y,z = u/np.sqrt(u2)
    return 0,x,y,z
  
  w = k_cos_theta + k
  x,y,z = np.cross(u,v)
  return normalized(np.array((w,x,y,z)))
    
#prepare blender and the scene
preparescene()


mat = bpy.data.materials.new(name="red")
mat.diffuse_color=(1.0,0.0,0.0)
mat.use_shadeless=True

targetpos=np.array([1.0,-.3,.9])
ex = np.array((1.0,0.0,0.0))
ey = np.array((0.0,1.0,0.0))
ez = np.array((0.0,0.0,1.0))
to = arrow(targetpos,(0.3,0.0,0.0),0.1, mat)

w,x,y,z = getquatrot(-ez,targetpos)
quat = mathutils.Quaternion([w,x,y,z])

po = arrow((0,0,0),(1.0,0.0,0.0),0.1, mat)
po.rotation_mode="QUATERNION"
po.rotation_quaternion = quat


mat = bpy.data.materials.new(name="white")
mat.diffuse_color=(1.0,1.0,1.0)
mat.use_shadeless=True
axis3d(mat)
addcamera(np.array((1.0,0.5,1.0))*2)
do_render_opengl()

"""
def main(args):
  try:
  except:
    print("Unexpected error:", sys.exc_info()[0])
    raise
    return 1  # exit on error
  else:
    return 0  # exit errorlessly
       
if __name__ == '__main__':
  sys.exit(main(sys.argv))
"""  
  
#blender -b seher.blend -P rendersat.py render
