bl_info = {
    "name": "CentroidOnBlender",
    "author": "Cicero Moraes",
    "version": (1, 1, 12),
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
import platform
import os
from math import sqrt
from mathutils import Matrix,Vector
from bpy_extras.object_utils import AddObjectHelper, object_data_add

from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )

def abrir_diretorio_relat(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])

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

    @classmethod
    def poll(cls, context):

        found = 'CENTR_MAX_TRI_DIGI' in bpy.data.objects

        if found == False:
            return True
        else:
            if found == True:
                return False

    def execute(self, context):
        CriaTriCentroideDef(self, "Max-IC-digi","Max-PMD-digi", "Max-PME-digi", "CENTR_MAX_TRI_DIGI", "CentroideMaxilaDigi")

        return {'FINISHED'}


class AdicionaMaxICdigi(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_max_ic_digi"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):

        found = 'Max-IC-digi' in bpy.data.objects

        if found == False:
            return True
        else:
            if found == True:
                return False

    def execute(self, context):
        AdicionaEMPTYDef("Max-IC-digi")
        return {'FINISHED'}
    
class AdicionaMaxPMDdigi(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_max_pmd_digi"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):

        found = 'Max-PMD-digi' in bpy.data.objects

        if found == False:
            return True
        else:
            if found == True:
                return False

    def execute(self, context):
        AdicionaEMPTYDef("Max-PMD-digi")
        return {'FINISHED'}
    
class AdicionaMaxPMEdigi(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_max_pme_digi"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):

        found = 'Max-PME-digi' in bpy.data.objects

        if found == False:
            return True
        else:
            if found == True:
                return False

    def execute(self, context):
        AdicionaEMPTYDef("Max-PME-digi")
        return {'FINISHED'}    


# PÓS-DIGITAL MANDÍBULA
    
class CriaTriCentroideManDigi(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_tri_centroide_man_digi"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):

        found = 'CENTR_MAND_TRI_DIGI' in bpy.data.objects

        if found == False:
            return True
        else:
            if found == True:
                return False

    def execute(self, context):
        CriaTriCentroideDef(self, "Man-IC-digi","Man-PMD-digi", "Man-PME-digi", "CENTR_MAND_TRI_DIGI", "CentroideMandibulaDigi")

        return {'FINISHED'}


class AdicionaManICdigi(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_man_ic_digi"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):

        found = 'Man-IC-digi' in bpy.data.objects

        if found == False:
            return True
        else:
            if found == True:
                return False

    def execute(self, context):
        AdicionaEMPTYDef("Man-IC-digi")
        return {'FINISHED'}
    
class AdicionaManPMDdigi(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_man_pmd_digi"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):

        found = 'Man-PMD-digi' in bpy.data.objects

        if found == False:
            return True
        else:
            if found == True:
                return False

    def execute(self, context):
        AdicionaEMPTYDef("Man-PMD-digi")
        return {'FINISHED'}
    
class AdicionaManPMEdigi(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_man_pme_digi"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):

        found = 'Man-PME-digi' in bpy.data.objects

        if found == False:
            return True
        else:
            if found == True:
                return False

    def execute(self, context):
        AdicionaEMPTYDef("Man-PME-digi")
        return {'FINISHED'}

# PÓS-REAL

# PÓS-REAL MAXILA

class CriaTriCentroideMaxReal(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_tri_centroide_max_real"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):

        found = 'CENTR_MAX_TRI_REAL' in bpy.data.objects

        if found == False:
            return True
        else:
            if found == True:
                return False

    def execute(self, context):
        CriaTriCentroideDef(self, "Max-IC-real","Max-PMD-real", "Max-PME-real", "CENTR_MAX_TRI_REAL", "CentroideMaxilaReal")

        return {'FINISHED'}


class AdicionaMaxICreal(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_max_ic_real"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):

        found = 'Max-IC-real' in bpy.data.objects

        if found == False:
            return True
        else:
            if found == True:
                return False

    def execute(self, context):
        AdicionaEMPTYDef("Max-IC-real")
        return {'FINISHED'}
    
class AdicionaMaxPMDreal(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_max_pmd_real"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):

        found = 'Max-PMD-real' in bpy.data.objects

        if found == False:
            return True
        else:
            if found == True:
                return False

    def execute(self, context):
        AdicionaEMPTYDef("Max-PMD-real")
        return {'FINISHED'}
    
class AdicionaMaxPMEreal(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_max_pme_real"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):

        found = 'Max-PME-real' in bpy.data.objects

        if found == False:
            return True
        else:
            if found == True:
                return False

    def execute(self, context):
        AdicionaEMPTYDef("Max-PME-real")
        return {'FINISHED'}    

# PÓS-REAL MANDÍBULA
    
class CriaTriCentroideManReal(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_tri_centroide_man_real"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):

        found = 'CENTR_MAND_TRI_REAL' in bpy.data.objects

        if found == False:
            return True
        else:
            if found == True:
                return False

    def execute(self, context):
        CriaTriCentroideDef(self, "Man-IC-real","Man-PMD-real", "Man-PME-real", "CENTR_MAND_TRI_REAL", "CentroideMandibulaReal")

        return {'FINISHED'}


class AdicionaManICreal(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_man_ic_real"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):

        found = 'Man-IC-real' in bpy.data.objects

        if found == False:
            return True
        else:
            if found == True:
                return False

    def execute(self, context):
        AdicionaEMPTYDef("Man-IC-real")
        return {'FINISHED'}
    
class AdicionaManPMDreal(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_man_pmd_real"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):

        found = 'Man-PMD-real' in bpy.data.objects

        if found == False:
            return True
        else:
            if found == True:
                return False

    def execute(self, context):
        AdicionaEMPTYDef("Man-PMD-real")
        return {'FINISHED'}
    
class AdicionaManPMEreal(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "mesh.add_man_pme_real"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):

        found = 'Man-PME-real' in bpy.data.objects

        if found == False:
            return True
        else:
            if found == True:
                return False

    def execute(self, context):
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
    MaxICreal = bpy.data.objects["Max-IC-real"]
    MaxPMDdigi = bpy.data.objects["Max-PMD-digi"]
    MaxPMDreal = bpy.data.objects["Max-PMD-real"]
    MaxPMEdigi = bpy.data.objects["Max-PME-digi"]
    MaxPMEreal = bpy.data.objects["Max-PME-real"]
    CentroideMaxilaDigi = bpy.data.objects["CentroideMaxilaDigi"] 
    CentroideMaxilaReal = bpy.data.objects["CentroideMaxilaReal"]

    DistMaxICDigiReal = DistanciaLinear("Max-IC-digi", "Max-IC-real")
    DistMaxPMDDigiReal = DistanciaLinear("Max-PMD-digi", "Max-PMD-real")
    DistMaxPMEDigiReal = DistanciaLinear("Max-PME-digi", "Max-PME-real")
    DistCentrMaxDigiReal = DistanciaLinear("CentroideMaxilaDigi", "CentroideMaxilaReal")

    ManICdigi = bpy.data.objects["Man-IC-digi"]
    ManICreal = bpy.data.objects["Man-IC-real"]
    ManPMDdigi = bpy.data.objects["Man-PMD-digi"]
    ManPMDreal = bpy.data.objects["Man-PMD-real"]
    ManPMEdigi = bpy.data.objects["Man-PME-digi"]
    ManPMEreal = bpy.data.objects["Man-PME-real"]
    CentroideMandibulaDigi = bpy.data.objects["CentroideMandibulaDigi"] 
    CentroideMandibulaReal = bpy.data.objects["CentroideMandibulaReal"]

    DistManICDigiReal = DistanciaLinear("Man-IC-digi", "Man-IC-real")
    DistManPMDDigiReal = DistanciaLinear("Man-PMD-digi", "Man-PMD-real")
    DistManPMEDigiReal = DistanciaLinear("Man-PME-digi", "Man-PME-real")
    DistCentrManDigiReal = DistanciaLinear("CentroideMandibulaDigi", "CentroideMandibulaReal")      

    bpy.ops.object.select_all(action='DESELECT')    

   
    #Ajusta a rotação -- não é necessário selecionar!


    bpy.data.objects["CentroideMaxilaDigi"].rotation_mode='AXIS_ANGLE'
    bpy.data.objects["CentroideMaxilaDigi"].rotation_mode='ZYX'
    bpy.data.objects["CentroideMaxilaReal"].rotation_mode='AXIS_ANGLE'
    bpy.data.objects["CentroideMaxilaReal"].rotation_mode='ZYX'

    bpy.data.objects["CentroideMandibulaDigi"].rotation_mode='AXIS_ANGLE'
    bpy.data.objects["CentroideMandibulaDigi"].rotation_mode='ZYX'
    bpy.data.objects["CentroideMandibulaReal"].rotation_mode='AXIS_ANGLE'
    bpy.data.objects["CentroideMandibulaReal"].rotation_mode='ZYX'


    with open(tmpdir+'/centroid_file.csv', mode='w') as centroid_file:
        centroid_writer = csv.writer(centroid_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        centroid_writer.writerow(['TABELA 01 - PONTOS ANATÔMICOS'])
        centroid_writer.writerow(['ID', 'LocX', 'LocY', 'LocZ'])

        centroid_writer.writerow(['Max-IC-Digi', str(MaxICdigi.location[0]), str(MaxICdigi.location[1]), str(MaxICdigi.location[2]) ])
        centroid_writer.writerow(['Max-IC-Real', str(MaxICreal.location[0]), str(MaxICreal.location[1]), str(MaxICreal.location[2]) ])
        centroid_writer.writerow(['Max-PMD-Digi', str(MaxPMDdigi.location[0]), str(MaxPMDdigi.location[1]), str(MaxPMDdigi.location[2]) ])
        centroid_writer.writerow(['Max-PMD-Real', str(MaxPMDreal.location[0]), str(MaxPMDreal.location[1]), str(MaxPMDreal.location[2]) ])
        centroid_writer.writerow(['Max-PME-Digi', str(MaxPMEdigi.location[0]), str(MaxPMEdigi.location[1]), str(MaxPMEdigi.location[2]) ])
        centroid_writer.writerow(['Max-PME-Real', str(MaxPMEreal.location[0]), str(MaxPMEreal.location[1]), str(MaxPMEreal.location[2]) ])
        centroid_writer.writerow([''])
        centroid_writer.writerow(['Man-IC-Digi', str(ManICdigi.location[0]), str(ManICdigi.location[1]), str(ManICdigi.location[2]) ])
        centroid_writer.writerow(['Man-IC-Real', str(ManICreal.location[0]), str(ManICreal.location[1]), str(ManICreal.location[2]) ])
        centroid_writer.writerow(['Man-PMD-Digi', str(ManPMDdigi.location[0]), str(ManPMDdigi.location[1]), str(ManPMDdigi.location[2]) ])
        centroid_writer.writerow(['Man-PMD-Real', str(ManPMDreal.location[0]), str(ManPMDreal.location[1]), str(ManPMDreal.location[2]) ])
        centroid_writer.writerow(['Man-PME-Digi', str(ManPMEdigi.location[0]), str(ManPMEdigi.location[1]), str(ManPMEdigi.location[2]) ])
        centroid_writer.writerow(['Man-PME-Real', str(ManPMEreal.location[0]), str(ManPMEreal.location[1]), str(ManPMEreal.location[2]) ])

        centroid_writer.writerow([''])
        centroid_writer.writerow(['TABELA 02 - CENTRÓIDES', 'Atencão eixos Rot!'])
        centroid_writer.writerow(['ID', 'LocX', 'LocY', 'LocZ', 'RotZ', 'RotY', 'RotX'])
        centroid_writer.writerow(['CentroideMaxilaDigi', str(CentroideMaxilaDigi.location[0]), str(CentroideMaxilaDigi.location[1]), str(CentroideMaxilaDigi.location[2]), str(math.degrees(CentroideMaxilaDigi.rotation_euler[0])), str(math.degrees(CentroideMaxilaDigi.rotation_euler[1])), str(math.degrees(CentroideMaxilaDigi.rotation_euler[2])) ])

        centroid_writer.writerow(['CentroideMaxilaReal', str(CentroideMaxilaReal.location[0]), str(CentroideMaxilaReal.location[1]), str(CentroideMaxilaReal.location[2]), str(math.degrees(CentroideMaxilaReal.rotation_euler[0])), str(math.degrees(CentroideMaxilaReal.rotation_euler[1])), str(math.degrees(CentroideMaxilaReal.rotation_euler[2])) ])        

        centroid_writer.writerow([''])

        centroid_writer.writerow(['CentroideMandibulaDigi', str(CentroideMandibulaDigi.location[0]), str(CentroideMandibulaDigi.location[1]), str(CentroideMandibulaDigi.location[2]), str(math.degrees(CentroideMandibulaDigi.rotation_euler[0])), str(math.degrees(CentroideMandibulaDigi.rotation_euler[1])), str(math.degrees(CentroideMandibulaDigi.rotation_euler[2])) ])

        centroid_writer.writerow(['CentroideMandibulaReal', str(CentroideMandibulaReal.location[0]), str(CentroideMandibulaReal.location[1]), str(CentroideMandibulaReal.location[2]), str(math.degrees(CentroideMandibulaReal.rotation_euler[0])), str(math.degrees(CentroideMandibulaReal.rotation_euler[1])), str(math.degrees(CentroideMandibulaReal.rotation_euler[2])) ])

        centroid_writer.writerow([''])
        centroid_writer.writerow(['TABELA 03 - DISTÂNCIAS'])
        centroid_writer.writerow(['IC-MaxDigi-MaxReal', str(DistMaxICDigiReal) ])
        centroid_writer.writerow(['PMD-MaxDigi-MaxReal', str(DistMaxPMDDigiReal) ])
        centroid_writer.writerow(['PME-MaxDigi-MaxReal', str(DistMaxPMEDigiReal) ])
        centroid_writer.writerow([''])
        centroid_writer.writerow(['IC-ManDigi-ManReal', str(DistManICDigiReal) ])
        centroid_writer.writerow(['PMD-ManDigi-ManReal', str(DistManPMDDigiReal) ])
        centroid_writer.writerow(['PME-ManDigi-ManReal', str(DistManPMEDigiReal) ])
        centroid_writer.writerow([''])
        centroid_writer.writerow(['Centroide-MaxDigi-MaxReal', str(DistCentrMaxDigiReal) ])
        centroid_writer.writerow(['Centroide-ManDigi-ManReal', str(DistCentrManDigiReal) ])

        centroid_writer.writerow([''])
        centroid_writer.writerow(['TABELA 04 - DIFERENCAS', 'Atencão eixos Rot!'])
        centroid_writer.writerow(['ID', 'RotZ', 'RotY', 'RotX'])

        centroid_writer.writerow(['Centroide-MaxDigi-MaxReal', str(abs(math.degrees(CentroideMaxilaDigi.rotation_euler[0]))-abs(math.degrees(CentroideMaxilaReal.rotation_euler[0]))), str(abs(math.degrees(CentroideMaxilaDigi.rotation_euler[1]))-abs(math.degrees(CentroideMaxilaReal.rotation_euler[1]))), str(abs(math.degrees(CentroideMaxilaDigi.rotation_euler[2]))-abs(math.degrees(CentroideMaxilaReal.rotation_euler[2]))) ])
        centroid_writer.writerow(['Centroide-ManDigi-ManReal', str(abs(math.degrees(CentroideMandibulaDigi.rotation_euler[0]))-abs(math.degrees(CentroideMandibulaReal.rotation_euler[0]))), str(abs(math.degrees(CentroideMandibulaDigi.rotation_euler[1]))-abs(math.degrees(CentroideMandibulaReal.rotation_euler[1]))), str(abs(math.degrees(CentroideMandibulaDigi.rotation_euler[2]))-abs(math.degrees(CentroideMandibulaReal.rotation_euler[2]))) ])

        centroid_writer.writerow([''])
        centroid_writer.writerow(['TABELA 05 - DIFERENCAS OUTROS PONTOS'])


        DistAREALDIGIORT = DistanciaLinear("A-REAL", "A-DIGIORT")
        DistICSREALDIGIORT = DistanciaLinear("ICS-REAL", "ICS-DIGIORT")
        DistICIREALDIGIORT = DistanciaLinear("ICI-REAL", "ICI-DIGIORT")
        DistBREALDIGIORT = DistanciaLinear("B-REAL", "B-DIGIORT")
        DistPogREALDIGIORT = DistanciaLinear("Pog-REAL", "Pog-DIGIORT")
        DistGnREALDIGIORT = DistanciaLinear("Gn-REAL", "Gn-DIGIORT")
        DistMeREALDIGIORT = DistanciaLinear("Me-REAL", "Me-DIGIORT")

        centroid_writer.writerow(["A'-REAL - A'-DIGI", str(DistAREALDIGIORT)])
        centroid_writer.writerow(["ICS-REAL - ICS-DIGI", str(DistICSREALDIGIORT)])
        centroid_writer.writerow(["ICI-REAL - ICI-DIGI", str(DistICIREALDIGIORT)])
        centroid_writer.writerow(["B'-REAL - B'-DIGI", str(DistBREALDIGIORT)])
        centroid_writer.writerow(["Pog'-REAL - Pog'-DIGI", str(DistPogREALDIGIORT)])
        centroid_writer.writerow(["Gn'-REAL - Gn'-DIGI", str(DistGnREALDIGIORT)])
        centroid_writer.writerow(["Me'-REAL - Me'-DIGI", str(DistMeREALDIGIORT)])


        subprocess.Popen("libreoffice "+tmpdir+"/centroid_file.csv", shell=True)
        abrir_diretorio_relat(tmpdir)

class GeraCSV(Operator, AddObjectHelper):
    """Create a new Mesh Object"""
    bl_idname = "object.gera_csv"
    bl_label = "Add Centroide"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        GeraCSVDef()
        return {'FINISHED'}
    
class BotoesMaxDigi(bpy.types.Panel):
    """Planejamento de cirurgia ortognática no Blender"""
    bl_label = "MAXILA DIGITAL"
    bl_idname = "max.digi"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Centroide"

    def draw(self, context):
        layout = self.layout

        obj = context.object
       
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


class BotoesMaxReal(bpy.types.Panel):
    """Planejamento de cirurgia ortognática no Blender"""
    bl_label = "MAXILA REAL"
    bl_idname = "max.real"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Centroide"

    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        row.operator("mesh.add_max_ic_real", text="Max-IC-real", icon="OUTLINER_DATA_EMPTY")
        
        row = layout.row()
        row.operator("mesh.add_max_pmd_real", text="Max-PMD-real", icon="OUTLINER_DATA_EMPTY")

        row = layout.row()
        row.operator("mesh.add_max_pme_real", text="Max-PME-real", icon="OUTLINER_DATA_EMPTY")

        row = layout.row()
        
        row = layout.row()
        row.operator("mesh.add_tri_centroide_max_real", text="Centróide Maxila Real", icon="MOD_DISPLACE")
        
class BotoesManDigi(bpy.types.Panel):
    """Planejamento de cirurgia ortognática no Blender"""
    bl_label = "MANDÍBULA DIGITAL"
    bl_idname = "man.digi"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Centroide"

    def draw(self, context):
        layout = self.layout

        obj = context.object
       
        row = layout.row()
        row.operator("mesh.add_man_ic_digi", text="Man-IC-digi", icon="OUTLINER_DATA_EMPTY")
        
        row = layout.row()
        row.operator("mesh.add_man_pmd_digi", text="Man-PMD-digi", icon="OUTLINER_DATA_EMPTY")

        row = layout.row()
        row.operator("mesh.add_man_pme_digi", text="Man-PME-digi", icon="OUTLINER_DATA_EMPTY")

        row = layout.row()
        
        row = layout.row()
        row.operator("mesh.add_tri_centroide_man_digi", text="Centróide Mandíbula Digi", icon="MOD_DISPLACE")


class BotoesManReal(bpy.types.Panel):
    """Planejamento de cirurgia ortognática no Blender"""
    bl_label = "MANDÍBULA REAL"
    bl_idname = "man.real"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Centroide"

    def draw(self, context):
        layout = self.layout

        obj = context.object
     
        row = layout.row()
        row.operator("mesh.add_man_ic_real", text="Man-IC-real", icon="OUTLINER_DATA_EMPTY")
        
        row = layout.row()
        row.operator("mesh.add_man_pmd_real", text="Man-PMD-real", icon="OUTLINER_DATA_EMPTY")

        row = layout.row()
        row.operator("mesh.add_man_pme_real", text="Man-PME-real", icon="OUTLINER_DATA_EMPTY")

        row = layout.row()
        
        row = layout.row()
        row.operator("mesh.add_tri_centroide_man_real", text="Centróide Mandíbula Real", icon="MOD_DISPLACE")

class BotoesDuroReal(bpy.types.Panel):
    """Planejamento de cirurgia ortognática no Blender"""
    bl_label = "PONTOS - REAL"
    bl_idname = "duro.real"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Centroide"

    def draw(self, context):
        layout = self.layout

        obj = context.object
     
        row = layout.row()
        row.operator("mesh.add_a_real", text="A'-REAL", icon="OUTLINER_DATA_EMPTY")

        row = layout.row()
        row.operator("mesh.add_ics_real", text="ICS-REAL", icon="OUTLINER_DATA_EMPTY")

        row = layout.row()
        row.operator("mesh.add_ici_real", text="ICI-REAL", icon="OUTLINER_DATA_EMPTY")     

        row = layout.row()
        row.operator("mesh.add_b_real", text="B'-REAL", icon="OUTLINER_DATA_EMPTY")

        row = layout.row()
        row.operator("mesh.add_pog_real", text="Pog'-REAL", icon="OUTLINER_DATA_EMPTY") 

        row = layout.row()
        row.operator("mesh.add_gn_real", text="Gn'-REAL", icon="OUTLINER_DATA_EMPTY")

        row = layout.row()
        row.operator("mesh.add_me_real", text="Me'-REAL", icon="OUTLINER_DATA_EMPTY")

class BotoesDuroDigi(bpy.types.Panel):
    """Planejamento de cirurgia ortognática no Blender"""
    bl_label = "PONTOS - DIGI"
    bl_idname = "duro.digi"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Centroide"

    def draw(self, context):
        layout = self.layout

        obj = context.object
     
        row = layout.row()
        row.operator("mesh.add_a_digiort", text="A'-DIGI", icon="OUTLINER_DATA_EMPTY")

        row = layout.row()
        row.operator("mesh.add_ics_digiort", text="ICS-DIGI", icon="OUTLINER_DATA_EMPTY")

        row = layout.row()
        row.operator("mesh.add_ici_digiort", text="ICI-DIGI", icon="OUTLINER_DATA_EMPTY")     

        row = layout.row()
        row.operator("mesh.add_b_digiort", text="B'-DIGI", icon="OUTLINER_DATA_EMPTY")

        row = layout.row()
        row.operator("mesh.add_pog_digiort", text="Pog'-DIGI", icon="OUTLINER_DATA_EMPTY") 

        row = layout.row()
        row.operator("mesh.add_gn_digiort", text="Gn'-DIGI", icon="OUTLINER_DATA_EMPTY")

        row = layout.row()
        row.operator("mesh.add_me_digiort", text="Me'-DIGI", icon="OUTLINER_DATA_EMPTY") 

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
    bpy.utils.register_class(CriaTriCentroideManDigi)
    bpy.utils.register_class(AdicionaManPMDdigi)
    bpy.utils.register_class(AdicionaManPMEdigi)
    bpy.utils.register_class(CriaTriCentroideMaxDigi)
    bpy.utils.register_class(AdicionaMaxICdigi)        
    bpy.utils.register_class(AdicionaMaxPMDdigi)
    bpy.utils.register_class(AdicionaMaxPMEdigi)
    bpy.utils.register_class(CriaTriCentroideManReal)
    bpy.utils.register_class(AdicionaManICreal)        
    bpy.utils.register_class(AdicionaManPMDreal)
    bpy.utils.register_class(AdicionaManPMEreal)
    bpy.utils.register_class(CriaTriCentroideMaxReal)
    bpy.utils.register_class(AdicionaMaxICreal)        
    bpy.utils.register_class(AdicionaMaxPMDreal)
    bpy.utils.register_class(AdicionaMaxPMEreal)
    bpy.utils.register_class(GeraCSV)
    bpy.utils.register_class(BotoesMaxDigi)
    bpy.utils.register_class(BotoesMaxReal)
    bpy.utils.register_class(BotoesManDigi)
    bpy.utils.register_class(BotoesManReal)
    bpy.utils.register_class(BotoesDuroReal)
    bpy.utils.register_class(BotoesDuroDigi)
    bpy.utils.register_class(BotoesTabela)
    
def unregister():
    bpy.utils.unregister_class(AdicionaManICdigi)
    bpy.utils.unregister_class(CriaTriCentroideManDigi)
    bpy.utils.unregister_class(AdicionaManPMDdigi)
    bpy.utils.unregister_class(AdicionaManPMEdigi)
    bpy.utils.unregister_class(CriaTriCentroideMaxDigi)
    bpy.utils.unregister_class(AdicionaMaxICdigi)        
    bpy.utils.unregister_class(AdicionaMaxPMDdigi)
    bpy.utils.unregister_class(AdicionaMaxPMEdigi)
    bpy.utils.unregister_class(CriaTriCentroideManReal)
    bpy.utils.unregister_class(AdicionaManICreal)        
    bpy.utils.unregister_class(AdicionaManPMDreal)
    bpy.utils.unregister_class(AdicionaManPMEreal)
    bpy.utils.unregister_class(CriaTriCentroideMaxReal)
    bpy.utils.unregister_class(AdicionaMaxICreal)        
    bpy.utils.unregister_class(AdicionaMaxPMDreal)
    bpy.utils.unregister_class(AdicionaMaxPMEreal)
    bpy.utils.unregister_class(GeraCSV)
    bpy.utils.unregister_class(BotoesMaxDigi)
    bpy.utils.unregister_class(BotoesMaxReal)
    bpy.utils.unregister_class(BotoesManDigi)
    bpy.utils.unregister_class(BotoesManReal)
    bpy.utils.unregister_class(BotoesDuroReal)
    bpy.utils.unregister_class(BotoesDuroDigi)
    bpy.utils.unregister_class(BotoesTabela)

if __name__ == "__main__":
    register()
