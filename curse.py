####################*###################*###################*###################*###################*###################
# 
####################*###################*###################*###################*###################*###################

import math
import numpy as np

from manim  import *
from math   import sqrt
from typing import List, Optional, Sequence, Tuple, Union
         
# unfortunately the space_ops version of this pure math function depends on renderer config!! this is a copy paste
# of the branch support arbitrary length lists without the config branch that assumes lists with exactly two elements.

def quatmult (
    *quats: Sequence[float],
) -> Union[np.ndarray, List[Union[float, np.ndarray]]]:
   if len(quats) == 0:
      return [1, 0, 0, 0]
   result = quats[0]
   for next_quat in quats[1:]:
      w1, x1, y1, z1 = result
      w2, x2, y2, z2 = next_quat
      result = [
         w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
         w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
         w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2,
         w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2,
      ]
   return result

class Ball4d(ThreeDScene):

   def construct(self):
      
      self.set_camera_orientation (
         theta = -90*DEGREES # unfortunately three_d_camera hardcodes a transform on the camera orientation. The details
       , phi   =   0*DEGREES # of the transform are below in the rotate function as we must apply the transform before
       , gamma =   0*DEGREES # our quaternion math to work in actual view space and then invert after our calculations.
       , zoom  = 0.5         # Then the hardcoded transform will put us back in actual view space. Yuck!
      )
 
      self.rotate(angle=10*DEGREES,axis=UP   ) # rotate away the overlap with the slice highlight
      self.rotate(angle=20*DEGREES,axis=RIGHT) # look slightly from above

      axes = ThreeDAxes (
         x_range=np.array([-6, 6, 2])
       , y_range=np.array([-6, 6, 2])
       , z_range=np.array([-6, 6, 2])
       , x_length=3
       , y_length=6
       , z_length=9
       , axis_config = {
          "stroke_color"  : WHITE
        , "stroke_width"  : 2
        , "include_tip"   : True
        , "include_ticks" : False
        , "tick_size"     : 0.05
       } ,
      ).scale(1.0)
    # self.add(axes) # useful for debugging

      offset = np.array([-1.5,0.5,0]) # moving the camera creates wonkiness with rotations so move the scene instead

      anim = ValueTracker(-1) 

      cube = Cube(side_length=10, color=WHITE, fill_opacity=0.0, stroke_width=2).move_to(offset)
      ball = Sphere(radius=5, color=BLUE, fill_opacity=0.5).move_to(offset)

      prism_out = Prism (
         dimensions=[0.1,10,10]
       , color=YELLOW, fill_opacity=0.0, stroke_width=1
      ).move_to(np.add(np.array([8,0,0]),offset))

      slice_out = always_redraw (
         lambda :
            Cylinder (
               radius=5*math.sqrt(max(0,1-anim.get_value()*anim.get_value()))
             , height=0.1
             , direction=np.array([1,0,0])
             , color=BLUE, fill_opacity=0.5
           ).move_to(np.add(np.array([8,0,0]),offset))
      )

      prism = always_redraw(
         lambda : Prism (
            dimensions=[0.1,10,10]
          , color=YELLOW, fill_opacity=0.5, stroke_width=0
         ).move_to(np.add(np.array([5*anim.get_value(),0,0]),offset))
      )

      self.play(FadeIn(cube), run_time=2)
      self.wait()

      self.play(FadeIn(ball), run_time=2)
      self.wait()

      self.add(prism)
      self.add(slice_out)
      self.add(prism_out)
      self.play(anim.animate.set_value(1), rate_func=linear, run_time=5)
      self.wait()

   def rotate (self, angle, axis):

      # burried within three_d_camera you will find this nasty hardcoded transform of the Euler angles:
      #
      # matrices = [
      #    rotation_about_z(-theta - 90 * DEGREES),
      #    rotation_matrix(-phi, RIGHT),
      #    rotation_about_z(gamma),
      # ]
      #
      # That breaks the symmetries of proper Euler angles. For example, in proper intrinsic Euler angles of zxz
      # (a,0,0) = (0,0,a). However, above (a,0,0) would instead equal (0,0,-a-90). x/phi is also negated. All this
      # means the math below completed breaks unless we first apply the above hardcoded transform to get into proper
      # Euler angles, do our math, then invert the transform to get into the hacked values that will then be hacked
      # back into proper angles by the hardcoding.

      # hacked camera angles that are hacked onproper euler angles zxz
      a1 = self.camera.get_theta()
      a2 = self.camera.get_phi  ()
      a3 = self.camera.get_gamma()

    # print("cam i",math.degrees(a1), " ",math.degrees(a2)," ",math.degrees(a3))

      # proper intrinsic euler angles zxz
      a1 = -a1-90*DEGREES
      a2 = -a2
      a3 =  a3

    # print("see i",math.degrees(a1), " ",math.degrees(a2)," ",math.degrees(a3))

      # combine the beginning orientation win the new rotation
      qt = quatmult(
         quaternion_from_angle_axis(a1,   OUT, axis_normalized=True),
         quaternion_from_angle_axis(a2, RIGHT, axis_normalized=True),
         quaternion_from_angle_axis(a3,   OUT, axis_normalized=True),
         quaternion_from_angle_axis(angle, axis, axis_normalized=True),
      )

    # print(qt)

      at, vt = angle_axis_from_quaternion(qt)
      mt = rotation_matrix(at,vt,homogeneous=False)
      mt = np.round(mt,3) # avoids numerical precision problems close to zero trig values

    # print(mt)
      
      c2 = mt[2][2]
      s2 = sqrt(1 - (mt[2][2])**2) # +/-
      a2 = np.arccos(mt[2][2])     # +/-

      eps = 0.0005

      if ( abs(s2) < eps ):
         # gimbal locked on x=0, z1 and z2 are denegerate so solve and assign it all to z1
         # use the angle addition formula for a1+a3 and assume a3 = 0
         # sin(A+B) = sin A cos B + cos A sin B
         # cos(A+B) = cos A cos B - sin A sin B
         s1 = mt[1][0]
         c1 = mt[0][0]
         a1 = np.arctan2(s1,c1)
         a3 = 0
       # print("gimbal lock")
      else:
         # here both +a2 and -a2 are possible solutions. Compute both and see which matches the rotation matrix.

         # compute for positive a2
         a1p = np.arctan2(+mt[0][2],-mt[1][2])
         a2p = a2
         a3p = np.arctan2(+mt[2][0],+mt[2][1])

         qtp = quatmult(
            quaternion_from_angle_axis(a1p,   OUT, axis_normalized=True),
            quaternion_from_angle_axis(a2p, RIGHT, axis_normalized=True),
            quaternion_from_angle_axis(a3p,   OUT, axis_normalized=True),
         )

         # compute for negative a2
         a1n = np.arctan2(-mt[0][2],+mt[1][2])
         a2n = -a2
         a3n = np.arctan2(-mt[2][0],-mt[2][1])
   
         qtn = quatmult(
            quaternion_from_angle_axis(a1n,   OUT, axis_normalized=True),
            quaternion_from_angle_axis(a2n, RIGHT, axis_normalized=True),
            quaternion_from_angle_axis(a3n,   OUT, axis_normalized=True),
         )

         # compute the arc length between correct quaternion and versions recontructed
         # from positive/negative assumptions for a2. Choose whichever is closest.
         qtc = quaternion_conjugate(qt)
         dtp = quatmult(qtc,qtp)
         dtn = quatmult(qtc,qtn)
         atp = 2*np.arctan2(dtp[1]**2+dtp[2]**2+dtp[3]**2,dtp[0])
         atn = 2*np.arctan2(dtn[1]**2+dtn[2]**2+dtn[3]**2,dtn[0])

       # print("see p",math.degrees(a1p), " ",math.degrees(a2p)," ",math.degrees(a3p))
       # print("see n",math.degrees(a1n), " ",math.degrees(a2n)," ",math.degrees(a3n))

         if ( abs(atn) < abs(atp) ) :
            a1 = a1n
            a2 = a2n
            a3 = a3n
         else:
            a1 = a1p
            a2 = a2p
            a3 = a3p
      
    # print("see o",math.degrees(a1), " ",math.degrees(a2)," ",math.degrees(a3))

      # transform from proper space to camera space. The hardcoded
      # transform will put us back into proper space.
      a1 = -(a1+90*DEGREES)
      a2 = -a2
      a3 =  a3

    # print("cam o",math.degrees(a1), " ",math.degrees(a2)," ",math.degrees(a3))

      self.camera.set_theta(a1)
      self.camera.set_phi  (a2)
      self.camera.set_gamma(a3)

