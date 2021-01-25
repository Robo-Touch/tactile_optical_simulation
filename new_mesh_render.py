from os.path import join
from os import path as osp

import mitsuba
mitsuba.set_variant("packet_rgb")
from mitsuba.core.xml import load_file
from mitsuba.core import Thread, LogLevel

logger = Thread.thread().logger()
logger.set_log_level(LogLevel.Warn)

from tactile_optical_simulation.scene_cfg_loading_utils import load_render_cfg
from tactile_optical_simulation.folder_utils import create_folder

cdir = osp.dirname(osp.abspath(__file__))

model_fn = join("models", "flatgel_with_mesh.xml")	
render_params_fn = join(cdir, "render_cfgs", "full_sensor_resolution.cfg")
_outdir = join("results", "new_mesh")

## filepath of new mesh. Absolute path is preferred
new_mesh_fn = join("models", "meshes", "gelpad.obj")
##

bname = osp.basename(new_mesh_fn)
mesh_bname, ext = osp.splitext(bname)

if ext != '.obj':
	print("Currently only obj mesh file format is supported")
	exit(1)

mesh_dname = osp.dirname(new_mesh_fn)
Thread.thread().file_resolver().append(mesh_dname)

dname = osp.dirname(model_fn)
Thread.thread().file_resolver().append(dname)
render_params = load_render_cfg(render_params_fn)
params = {
	"hfName" : mesh_bname
}
scene = load_file(model_fn, **render_params, **params)
integrator = scene.integrator()
cam = scene.sensors()[0]

create_folder(_outdir)

integrator.render(scene, cam)
film = cam.film()
outFn = join(_outdir, "outfile.exr")
film.set_destination_file(outFn)
film.develop()