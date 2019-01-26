bl_info = {
    "name": "CentroidOnBlender",
    "author": "Cicero Moraes",
    "version": (1, 1, 11),
    "blender": (2, 75, 0),
    "location": "View3D",
    "description": "Planejamento de Cirurgia Ortognática no Blender",
    "warning": "",
    "wiki_url": "",
    "category": "Mesh",
    }

import bpy
import bmesh
import fnmatch
import csv
import tempfile
import subprocess
import math
from math import sqrt
from mathutils import Matrix,Vector
from bpy_extras.object_utils import AddObjectHelper, object_data_add

from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )

def CriaTriCentroideDef(self, Ponto1, Ponto2, Ponto3, NomePlano, NomeCentroide):

    context = bpy.context
    obj = context.active_object
    scn = context.scene

# Seleciona os pontos de interesse

    bpy.ops.object.select_all(action='DESELECT')    

    Ponto01 = bpy.data.objects[Ponto1]
    Ponto02 = bpy.data.objects[Ponto2]
    Ponto03 = bpy.data.objects[Ponto3]
    
    Ponto01.select = True
    Ponto02.select = True
    Ponto03.select = True 
    bpy.context.scene.objects.active = Ponto01
    

    bpy.context.scene.cursor_location = (0.0, 0.0, 0.0)

# Cria a malha    

    verts = [Ponto01.location,
             Ponto02.location,
             Ponto03.location,
            ]

    edges = []
    faces = [[0, 1, 2, ],]

    mesh = bpy.data.meshes.new(name=NomePlano)
    mesh.from_pydata(verts, edges, faces)
    object_data_add(context, mesh, operator=self)
    
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
    
    bpy.ops.object.empty_add(type='PLAIN_AXES', radius=6, view_align=False, location=(0, 0, 0))
    bpy.context.object.name = NomeCentroide
    bpy.context.object.show_name = True
    

    bpy.ops.object.select_all(action='DESELECT')    
    Plano = bpy.data.objects[NomePlano]
    Plano.select = True
    bpy.context.scene.objects.active = Plano
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='TOGGLE')
    
    bpy.ops.mesh.select_mode(type="FACE")
#    bpy.ops.mesh.select_all(action='TOGGLE')
    
    
    obj = bpy.context.edit_object
    me = obj.data
    bm = bmesh.from_edit_mesh(me)
    
    bm.faces.ensure_lookup_table()

    mw = obj.matrix_world.copy()
    face = bm.faces[0]
    o = face.calc_center_median()
    
    axis_src = face.normal
    axis_src2 = face.calc_tangent_edge()
    axis_dst = Vector((0, 0, 1))
    axis_dst2 = Vector((0, 1, 0))

    vec2 = axis_src * obj.matrix_world.inverted()
    matrix_rotate = axis_dst.rotation_difference(vec2).to_matrix().to_4x4()

    vec1 = axis_src2 * obj.matrix_world.inverted()
    axis_dst2 = axis_dst2*matrix_rotate.inverted()
    mat_tmp = axis_dst2.rotation_difference(vec1).to_matrix().to_4x4()
    matrix_rotate = mat_tmp*matrix_rotate
    matrix_translation = Matrix.Translation(mw * o) #

    obj2 = context.scene.objects.get(NomeCentroide)
    obj2.matrix_world = matrix_translation * matrix_rotate.to_4x4()
    
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.object.show_name = True


def AdicionaEMPTYDef(Nome):

    bpy.ops.object.empty_add(type='PLAIN_AXES', radius=6, view_align=False)
    bpy.context.object.name = Nome
    bpy.context.object.show_name = True
    
    
# PÓS-DIGITAL MAXILA

class CriaTriCentroideMaxDigi(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_tri_centroide_max_digi"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        CriaTriCentroideDef(self, "Max-IC-digi","Max-PMD-digi", "Max-PME-digi", "CENTR_MAX_TRI_DIGI", "CentroideMaxilaDigi")

        return {'FINISHED'}


class AdicionaMaxICdigi(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_max_ic_digi"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.ops.object.select_all(action='DESELECT')    
        Pontos = [obj for obj in bpy.context.scene.objects if fnmatch.fnmatchcase(obj.name, "Max-IC-dig*")]
        for i in Pontos:
            i.select=True
        
        bpy.ops.object.delete(use_global=False)

        AdicionaEMPTYDef("Max-IC-digi")
        return {'FINISHED'}
    
class AdicionaMaxPMDdigi(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_max_pmd_digi"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.ops.object.select_all(action='DESELECT')    
        Pontos = [obj for obj in bpy.context.scene.objects if fnmatch.fnmatchcase(obj.name, "Max-PMD-dig*")]
        for i in Pontos:
            i.select=True
        
        bpy.ops.object.delete(use_global=False)

        AdicionaEMPTYDef("Max-PMD-digi")
        return {'FINISHED'}
    
class AdicionaMaxPMEdigi(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_max_pme_digi"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.ops.object.select_all(action='DESELECT')    
        Pontos = [obj for obj in bpy.context.scene.objects if fnmatch.fnmatchcase(obj.name, "Max-PME-dig*")]
        for i in Pontos:
            i.select=True
        
        bpy.ops.object.delete(use_global=False)

        AdicionaEMPTYDef("Max-PME-digi")
        return {'FINISHED'}    


# PÓS-DIGITAL MANDÍBULA
    
class CriaTriCentroideManDigi(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_tri_centroide_man_digi"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        CriaTriCentroideDef(self, "Man-IC-digi","Man-PMD-digi", "Man-PME-digi", "CENTR_MAND_TRI_DIGI", "CentroideMandibulaDigi")

        return {'FINISHED'}


class AdicionaManICdigi(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_man_ic_digi"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.ops.object.select_all(action='DESELECT')    
        Pontos = [obj for obj in bpy.context.scene.objects if fnmatch.fnmatchcase(obj.name, "Man-IC-dig*")]
        for i in Pontos:
            i.select=True
        
        bpy.ops.object.delete(use_global=False)

        AdicionaEMPTYDef("Man-IC-digi")
        return {'FINISHED'}
    
class AdicionaManPMDdigi(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_man_pmd_digi"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.ops.object.select_all(action='DESELECT')    
        Pontos = [obj for obj in bpy.context.scene.objects if fnmatch.fnmatchcase(obj.name, "Man-PMD-dig*")]
        for i in Pontos:
            i.select=True
        
        bpy.ops.object.delete(use_global=False)

        AdicionaEMPTYDef("Man-PMD-digi")
        return {'FINISHED'}
    
class AdicionaManPMEdigi(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_man_pme_digi"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.ops.object.select_all(action='DESELECT')    
        Pontos = [obj for obj in bpy.context.scene.objects if fnmatch.fnmatchcase(obj.name, "Man-PME-dig*")]
        for i in Pontos:
            i.select=True
        
        bpy.ops.object.delete(use_global=False)

        AdicionaEMPTYDef("Man-PME-digi")
        return {'FINISHED'}

# PÓS-REAL

# PÓS-REAL MAXILA

class CriaTriCentroideMaxReal(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_tri_centroide_max_real"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        CriaTriCentroideDef(self, "Max-IC-real","Max-PMD-real", "Max-PME-real", "CENTR_MAX_TRI_REAL", "CentroideMaxilaReal")

        return {'FINISHED'}


class AdicionaMaxICreal(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_max_ic_real"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.ops.object.select_all(action='DESELECT')    
        Pontos = [obj for obj in bpy.context.scene.objects if fnmatch.fnmatchcase(obj.name, "Max-IC-rea*")]
        for i in Pontos:
            i.select=True
        
        bpy.ops.object.delete(use_global=False)

        AdicionaEMPTYDef("Max-IC-real")
        return {'FINISHED'}
    
class AdicionaMaxPMDreal(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_max_pmd_real"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.ops.object.select_all(action='DESELECT')    
        Pontos = [obj for obj in bpy.context.scene.objects if fnmatch.fnmatchcase(obj.name, "Max-PMD-rea*")]
        for i in Pontos:
            i.select=True
        
        bpy.ops.object.delete(use_global=False)

        AdicionaEMPTYDef("Max-PMD-real")
        return {'FINISHED'}
    
class AdicionaMaxPMEreal(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_max_pme_real"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.ops.object.select_all(action='DESELECT')    
        Pontos = [obj for obj in bpy.context.scene.objects if fnmatch.fnmatchcase(obj.name, "Max-PME-rea*")]
        for i in Pontos:
            i.select=True
        
        bpy.ops.object.delete(use_global=False)

        AdicionaEMPTYDef("Max-PME-real")
        return {'FINISHED'}    

# PÓS-REAL MANDÍBULA
    
class CriaTriCentroideManReal(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_tri_centroide_man_real"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        CriaTriCentroideDef(self, "Man-IC-real","Man-PMD-real", "Man-PME-real", "CENTR_MAND_TRI_REAL", "CentroideMandibulaReal")

        return {'FINISHED'}


class AdicionaManICreal(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_man_ic_real"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.ops.object.select_all(action='DESELECT')    
        Pontos = [obj for obj in bpy.context.scene.objects if fnmatch.fnmatchcase(obj.name, "Man-IC-rea*")]
        for i in Pontos:
            i.select=True
        
        bpy.ops.object.delete(use_global=False)

        AdicionaEMPTYDef("Man-IC-real")
        return {'FINISHED'}
    
class AdicionaManPMDreal(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_man_pmd_real"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.ops.object.select_all(action='DESELECT')    
        Pontos = [obj for obj in bpy.context.scene.objects if fnmatch.fnmatchcase(obj.name, "Man-PMD-rea*")]
        for i in Pontos:
            i.select=True
        
        bpy.ops.object.delete(use_global=False)

        AdicionaEMPTYDef("Man-PMD-real")
        return {'FINISHED'}
    
class AdicionaManPMEreal(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_man_pme_real"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        bpy.ops.object.select_all(action='DESELECT')    
        Pontos = [obj for obj in bpy.context.scene.objects if fnmatch.fnmatchcase(obj.name, "Man-PME-rea*")]
        for i in Pontos:
            i.select=True
        
        bpy.ops.object.delete(use_global=False)

        AdicionaEMPTYDef("Man-PME-real")
        return {'FINISHED'}

def DistanciaLinear(Objeto1, Objeto2):

    l = []
    Objetos = [bpy.data.objects[Objeto1], bpy.data.objects[Objeto2]]
    
    for item in Objetos:
       l.append(item.location)

    distanciaLinear = sqrt( (l[0][0] - l[1][0])**2 + (l[0][1] - l[1][1])**2 + (l[0][2] - l[1][2])**2)
    
    return distanciaLinear


def GeraCSVDef():

    tmpdir = tempfile.mkdtemp()    

    MaxICdigi = bpy.data.objects["Max-IC-digi"]
    CentroideMaxilaDigi = bpy.data.objects["CentroideMaxilaDigi"] 
    CentroideMaxilaReal = bpy.data.objects["CentroideMaxilaReal"]

    DistMaxDigiReal = DistanciaLinear("CentroideMaxilaDigi", "CentroideMaxilaReal")       

    bpy.ops.object.select_all(action='DESELECT')    

   
    #Ajusta a rotação -- não é necessário selecionar!


    bpy.data.objects["CentroideMaxilaDigi"].rotation_mode='AXIS_ANGLE'
    bpy.data.objects["CentroideMaxilaDigi"].rotation_mode='ZYX'
    bpy.data.objects["CentroideMaxilaReal"].rotation_mode='AXIS_ANGLE'
    bpy.data.objects["CentroideMaxilaReal"].rotation_mode='ZYX'


    with open(tmpdir+'/centroid_file.csv', mode='w') as centroid_file:
        centroid_writer = csv.writer(centroid_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        centroid_writer.writerow(['TABELA 01 - POSIÇÃO E ROTAÇÃO'])
        centroid_writer.writerow(['ID', 'LocX', 'LocY', 'LocZ', 'RotX', 'RotY', 'RotZ'])

        centroid_writer.writerow(['Max-IC-Digi', str(MaxICdigi.location[0]), str(MaxICdigi.location[1]), str(MaxICdigi.location[2]) ])

        centroid_writer.writerow(['CentroideMaxilaDigi', str(CentroideMaxilaDigi.location[0]), str(CentroideMaxilaDigi.location[1]), str(CentroideMaxilaDigi.location[2]), str(math.degrees(CentroideMaxilaDigi.rotation_euler[0])), str(math.degrees(CentroideMaxilaDigi.rotation_euler[1])), str(math.degrees(CentroideMaxilaDigi.rotation_euler[2])) ])

        centroid_writer.writerow(['CentroideMaxilaReal', str(CentroideMaxilaReal.location[0]), str(CentroideMaxilaReal.location[1]), str(CentroideMaxilaReal.location[2]), str(math.degrees(CentroideMaxilaReal.rotation_euler[0])), str(math.degrees(CentroideMaxilaReal.rotation_euler[1])), str(math.degrees(CentroideMaxilaReal.rotation_euler[2])) ])        

        centroid_writer.writerow([''])
        centroid_writer.writerow(['TABELA 02 - DISTÂNCIAS'])
        centroid_writer.writerow(['MaxDigi-MaxReal', str(DistMaxDigiReal) ])

        centroid_writer.writerow([''])
        centroid_writer.writerow(['TABELA 03 - DIFERENCAS', 'RotX', 'RotY', 'RotZ'])

        centroid_writer.writerow(['MaxDigi-MaxReal', str(abs(math.degrees(CentroideMaxilaDigi.rotation_euler[0]))-abs(math.degrees(CentroideMaxilaReal.rotation_euler[0]))), str(abs(math.degrees(CentroideMaxilaDigi.rotation_euler[1]))-abs(math.degrees(CentroideMaxilaReal.rotation_euler[1]))), str(abs(math.degrees(CentroideMaxilaDigi.rotation_euler[2]))-abs(math.degrees(CentroideMaxilaReal.rotation_euler[2]))) ])

        subprocess.Popen("libreoffice "+tmpdir+"/centroid_file.csv", shell=True)

class GeraCSV(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "object.gera_csv"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        GeraCSVDef()
        return {'FINISHED'}
    
class BotoesCentroideDigi(bpy.types.Panel):
    """Planejamento de cirurgia ortognática no Blender"""
    bl_label = "PÓS-DIGITAL"
    bl_idname = "xxxx.aaa"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Centroide"

    def draw(self, context):
        layout = self.layout

        obj = context.object

        # Maxila Digital
        
        row = layout.row()
        row.label(text="MAXILA DIGITAL")
        
        row = layout.row()
        row.operator("mesh.add_max_ic_digi", text="Max-IC-digi", icon="OUTLINER_DATA_EMPTY")
        
        row = layout.row()
        row.operator("mesh.add_max_pmd_digi", text="Max-PMD-digi", icon="OUTLINER_DATA_EMPTY")

        row = layout.row()
        row.operator("mesh.add_max_pme_digi", text="Max-PME-digi", icon="OUTLINER_DATA_EMPTY")

        row = layout.row()
        
        row = layout.row()
        row.operator("mesh.add_tri_centroide_max_digi", text="Centróide Maxila Digi", icon="MOD_DISPLACE")

        row = layout.row()

        # Mandíbula Digital
        
        row = layout.row()
        row.label(text="MANDÍBULA DIGITAL")
        
        row = layout.row()
        row.operator("mesh.add_man_ic_digi", text="Man-IC-digi", icon="OUTLINER_DATA_EMPTY")
        
        row = layout.row()
        row.operator("mesh.add_man_pmd_digi", text="Man-PMD-digi", icon="OUTLINER_DATA_EMPTY")

        row = layout.row()
        row.operator("mesh.add_man_pme_digi", text="Man-PME-digi", icon="OUTLINER_DATA_EMPTY")

        row = layout.row()
        
        row = layout.row()
        row.operator("mesh.add_tri_centroide_man_digi", text="Centróide Mandíbula Digi", icon="MOD_DISPLACE")


        
class BotoesCentroideReal(bpy.types.Panel):
    """Planejamento de cirurgia ortognática no Blender"""
    bl_label = "PÓS-REAL"
    bl_idname = "xxxx.aa"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Centroide"

    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        row.label(text="MAXILA REAL")
        
        row = layout.row()
        row.operator("mesh.add_max_ic_real", text="Max-IC-real", icon="OUTLINER_DATA_EMPTY")
        
        row = layout.row()
        row.operator("mesh.add_max_pmd_real", text="Max-PMD-real", icon="OUTLINER_DATA_EMPTY")

        row = layout.row()
        row.operator("mesh.add_max_pme_real", text="Max-PME-real", icon="OUTLINER_DATA_EMPTY")

        row = layout.row()
        
        row = layout.row()
        row.operator("mesh.add_tri_centroide_max_real", text="Centróide Maxila Real", icon="MOD_DISPLACE")

        row = layout.row()
        row.label(text="MANDÍBULA REAL")
        
        row = layout.row()
        row.operator("mesh.add_man_ic_real", text="Man-IC-real", icon="OUTLINER_DATA_EMPTY")
        
        row = layout.row()
        row.operator("mesh.add_man_pmd_real", text="Man-PMD-real", icon="OUTLINER_DATA_EMPTY")

        row = layout.row()
        row.operator("mesh.add_man_pme_real", text="Man-PME-real", icon="OUTLINER_DATA_EMPTY")

        row = layout.row()
        
        row = layout.row()
        row.operator("mesh.add_tri_centroide_man_real", text="Centróide Mandíbula Real", icon="MOD_DISPLACE")

class BotoesTabela(bpy.types.Panel):
    """Planejamento de cirurgia ortognática no Blender"""
    bl_label = "TABELA"
    bl_idname = "xxxx.aaaaa"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Centroide"

    def draw(self, context):
        layout = self.layout

        obj = context.object

#        row = layout.row()
#        row.label(text="MAXILA REAL")

        row = layout.row()
        row.operator("object.gera_csv", text="Gera Tabela!", icon="LINENUMBERS_OFF")                
    
def register():
    bpy.utils.register_class(AdicionaManICdigi)
    bpy.utils.register_class(BotoesCentroideDigi)
    bpy.utils.register_class(CriaTriCentroideManDigi)
    bpy.utils.register_class(AdicionaManPMDdigi)
    bpy.utils.register_class(AdicionaManPMEdigi)
    bpy.utils.register_class(CriaTriCentroideMaxDigi)
    bpy.utils.register_class(AdicionaMaxICdigi)        
    bpy.utils.register_class(AdicionaMaxPMDdigi)
    bpy.utils.register_class(AdicionaMaxPMEdigi)
    bpy.utils.register_class(BotoesCentroideReal)
    bpy.utils.register_class(CriaTriCentroideManReal)
    bpy.utils.register_class(AdicionaManICreal)        
    bpy.utils.register_class(AdicionaManPMDreal)
    bpy.utils.register_class(AdicionaManPMEreal)
    bpy.utils.register_class(CriaTriCentroideMaxReal)
    bpy.utils.register_class(AdicionaMaxICreal)        
    bpy.utils.register_class(AdicionaMaxPMDreal)
    bpy.utils.register_class(AdicionaMaxPMEreal)
    bpy.utils.register_class(GeraCSV)
    bpy.utils.register_class(BotoesTabela)
    
def unregister():
    bpy.utils.unregister_class(AdicionaManICdigi)
    bpy.utils.unregister_class(BotoesCentroideDigi)
    bpy.utils.unregister_class(CriaTriCentroideManDigi)
    bpy.utils.unregister_class(AdicionaManPMDdigi)
    bpy.utils.unregister_class(AdicionaManPMEdigi)
    bpy.utils.unregister_class(CriaTriCentroideMaxDigi)
    bpy.utils.unregister_class(AdicionaMaxICdigi)        
    bpy.utils.unregister_class(AdicionaMaxPMDdigi)
    bpy.utils.unregister_class(AdicionaMaxPMEdigi)
    bpy.utils.unregister_class(BotoesCentroideReal)
    bpy.utils.unregister_class(CriaTriCentroideManReal)
    bpy.utils.unregister_class(AdicionaManICreal)        
    bpy.utils.unregister_class(AdicionaManPMDreal)
    bpy.utils.unregister_class(AdicionaManPMEreal)
    bpy.utils.unregister_class(CriaTriCentroideMaxReal)
    bpy.utils.unregister_class(AdicionaMaxICreal)        
    bpy.utils.unregister_class(AdicionaMaxPMDreal)
    bpy.utils.unregister_class(AdicionaMaxPMEreal)
    bpy.utils.unregister_class(GeraCSV)
    bpy.utils.unregister_class(BotoesTabela)

if __name__ == "__main__":
    register()
