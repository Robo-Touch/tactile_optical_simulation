from mitsuba.core import *
from mitsuba.render import RenderQueue, RenderJob, SceneHandler
import multiprocessing
from os import path as osp
from os.path import join

from tactile_optical_simulation.scene_cfg_loading_utils import load_render_cfg, load_img_with_cfg, load_scene_from_params

# Load file list 
from file_list_cfgs.flatgel import fname, img_list, project_name

# Get a reference to the thread's file resolver
fileResolver = Thread.getThread().getFileResolver()
# Register any searchs path needed to load scene resources (optional)
dname = osp.dirname(fname)
fileResolver.appendPath(dname)

# load render params
render_params = load_render_cfg(join("render_cfgs", "focussed.cfg"))
loading_param_list, target_im_list = load_img_with_cfg(img_list, render_params)

for scene_id, params in enumerate(loading_param_list):
  print(f"Rendering {scene_id}/{len(loading_param_list)} fn:{params['baseFn']}")

  paramMap = StringMap()
  for k in render_params:
    print(f"{k}: {render_params[k]}")
    paramMap[k] = str(render_params[k])

  for k in params:
    print(f"{k}: {params[k]}")
    paramMap[k] = str(params[k])

  # Load the scene from an XML file
  scene = SceneHandler.loadScene(fileResolver.resolve(fname), paramMap)

  outFn = f"{params['baseFn']}_sim.exr"
  outFn = join("results", "flatgel", outFn)
  
  scheduler = Scheduler.getInstance()
  # Start up the scheduling system with one worker per local core
  for i in range(0, multiprocessing.cpu_count()):
    scheduler.registerWorker(LocalWorker(i, 'wrk%i' % i))
  scheduler.start()
  # Create a queue for tracking render jobs
  queue = RenderQueue()
  scene.setDestinationFile(outFn)
  # Create a render job and insert it into the queue
  job = RenderJob('myRenderJob', scene, queue)
  job.start()
  # Wait for all jobs to finish and release resources

  queue.waitLeft(0)
  queue.join()
  # Print some statistics about the rendering process
  print(Statistics.getInstance().getStats())