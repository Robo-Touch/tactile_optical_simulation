import mitsuba
import enoki as ek
from math import radians, cos
from mitsuba.core import (Point3f, warp, Ray3f,
            Bitmap, AnimatedTransform, filesystem,
            Frame3f, Transform4f)
from mitsuba.core.math import Pi, InvFourPi
from mitsuba.render import (DirectionSample3f, Emitter,
    SurfaceInteraction3f, EmitterFlags,
    Texture)


class SpatialVaryingArea(Emitter):
  """docstring for MyPointEmitter"""
  def __init__(self, props):
    super(SpatialVaryingArea, self).__init__(props)

    self.m_radiance = props['radiance'] # assumption that a texture is returned
    self.m_flags = EmitterFlags.Surface | EmitterFlags.SpatiallyVarying

    # simple solution 
    self.cutOffAngle = radians(props['cutoff_angle'])
    self.cosTotalWidth = cos(self.cutOffAngle)
    self.cosFallOffStart = cos(radians(props['beam_width']))
    self.m_invTransitionWidth = 1.0/(self.cutOffAngle - radians(props['beam_width']))

  def set_shape_area(self):
    self.m_shape = super(SpatialVaryingArea, self).shape()
    assert(self.m_shape is not None)
    self.m_area_times = self.m_shape.surface_area()*Pi

  # not used in path integrator
  def sample_ray(self, time,
      sample1, # wavelength
      sample2, # pos
      sample3, # dir
      active):
    
    ps = self.m_shape.sample_position(time, sample2, active)
    local = warp.square_to_cosine_hemisphere(sample3)

    si = SurfaceInteraction3f(ps, 0)
    wavelengths, spec_weight = self.m_radiance.sample(si, ek.arange(sample1), active)
    
    ray = Ray3f(ps.p, Frame3f(ps.n).to_world(local), time, wavelengths)
    return (ray, spec_weight*self.m_area_times_pi)

  def sample_direction(self, ref, sample, active):
    # as the shape init happens after the emitter init
    if( not (hasattr(self, "m_shape"))):
      self.set_shape_area()

    ds = self.m_shape.sample_direction(ref, sample, active)
    
    active &= (ek.dot(ds.d, ds.n) < 0) & (ek.neq(ds.pdf, 0))
    
    si = SurfaceInteraction3f(ds, ref.wavelengths)
    # spatially varying
    cosTheta = -ek.dot(ds.d, ds.n)
    fall = self.fallof(cosTheta)
    
    spec = self.m_radiance.eval(si, active)*fall/ds.pdf 
    
    ds.object = 0 # HACK
    
    return (ds, ek.select(active, spec, ek.zero(type(spec)) ))

  def fallof(self, cosTheta):
    # delta = (cosTheta - self.cosTotalWidth)/(self.cosFallOffStart - self.cosTotalWidth)
    delta = (self.cutOffAngle - ek.acos(cosTheta))*self.m_invTransitionWidth
    delta = ek.select(cosTheta > self.cosFallOffStart, ek.full(type(delta), 1), delta)
    delta = ek.select(cosTheta < self.cosTotalWidth, ek.zero(type(delta)), delta)
    return delta
  
  def pdf_direction(self, ref, ds, active):
    # as the shape init happens after the emitter init
    if( not (hasattr(self, "m_shape"))):
      self.set_shape_area()
    tmp3 = ek.select(ek.dot(ds.d, ds.n) < 0, self.m_shape.pdf_direction(ref, ds, active), float(0))
    return tmp3
    
  def eval(self, si, active): 
    cosTheta = ek.dot(si.wi, si.n)
  
    tmp2 = ek.select(Frame3f.cos_theta(si.wi) > 0, \
            self.m_radiance.eval(si, active)*self.fallof(cosTheta), \
            float(0))
    return tmp2  

  def bbox(self):
    return self.m_shape.bbox()

  def to_string(self):
    mystr = "SpatialVaryingArea" + \
    "\n intensity " + str(self.m_radiance) + \
    "\n cosTotalWidth " + str(self.cosTotalWidth) + \
    "\n cosFallOffStart " + str(self.cosFallOffStart)
    return mystr

class MyPointEmitter(Emitter):
  """docstring for MyPointEmitter"""
  def __init__(self, props):
    super(MyPointEmitter, self).__init__(props)
    # Emitter.__init__(self, props)
    # Bug - have to query it once
    self.m_intensity = props['intensity'] # assumption that a texture is returned
    # self.m_intensity = Texture.D65(1)
    print(self.m_intensity)
    self.m_needs_sample_3 = False
    self.m_flags = +EmitterFlags.DeltaPosition

    # should ideally be inherited from cpp parent class
    self.m_world_transform = AnimatedTransform(props["to_world"])

  def sample_ray(self, time,
      sample1, # wavelength
      sample2, # pos
      sample3, # dir
      active):
    wavelengths, spec_weight = self.m_intensity.sample(SurfaceInteraction3f(), ek.arange(sample1), active)
    trafo = self.m_world_transform.eval(ref.time)
    ray = Ray3f(trafo*Point3f(0), warp.square_to_uniform_sphere(sample3),
        time, wavelengths)

    # print(spec_weight.class_().name())
    return (ray, spec_weight*4.0*Pi)

  def sample_direction(self, ref, sample, active):
    trafo = self.m_world_transform.eval(ref.time, active)

    ds = DirectionSample3f()
    ds.p = trafo.matrix[3][:3]
    ds.n = 0
    ds.uv = 0
    ds.time = ref.time
    ds.pdf = 1
    ds.delta = True
    ds.d = ds.p - ref.p
    ds.dist = ek.norm(ds.d)
    inv_dist = ek.rcp(ds.dist)
    ds.d *= inv_dist

    si = SurfaceInteraction3f()
    si.wavelengths = ref.wavelengths

    spec = self.m_intensity.eval(si, active)*(inv_dist*inv_dist)
    return (ds, spec)
  
  def pdf_direction(self, ref, ds, active):
    return 0

  def eval(self, si, active):
    return 0

  def bbox(self):
    return self.m_world_transform.translation_bounds()

  def to_string(self):
    mystr = "MyPointLight\n"
    mystr.append(" world_transform" + self.m_world_transform.to_string())
    mystr.append(" intensity" + self.m_intensity + "\n") 
    return mystr