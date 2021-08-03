---
title: mytiger.rag
hide:
  - navigation # Hide navigation
  - toc        # Hide table of contents
---

<div class="vboxlayout align-center justify-center" markdown=1>

![image](https://user-images.githubusercontent.com/2152766/114277217-36917500-9a22-11eb-9120-efc0c6b011e6.png)

A physicalised Ragcar.

</div>

```json
{
    "entities": {
        "1": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.5230555534362793, 
                                0.5230555534362793, 
                                0.5230555534362793, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ColorComponent"
                }, 
                "GeometryDescriptionComponent": {
                    "members": {
                        "extents": {
                            "type": "Vector3", 
                            "values": [
                                30.200000762939453, 
                                6.600000381469727, 
                                6.600002288818359
                            ]
                        }, 
                        "length": 23.600000381469727, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                3.5762786865234375e-07, 
                                -5.960464477539062e-07
                            ]
                        }, 
                        "radius": 3.299999952316284, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|environment_grp|pCylinder4", 
                        "shortestPath": "pCylinder4", 
                        "value": "rRigid14"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                -0.08376405398144993, 
                                -0.0041276343763886406, 
                                -0.9964770674205442, 
                                0.0, 
                                -0.04921719875688963, 
                                0.9987880993216353, 
                                -3.469446951953614e-18, 
                                0.0, 
                                0.9952694361865623, 
                                0.04904380988391943, 
                                -0.08386569086910578, 
                                0.0, 
                                -30.611989306450482, 
                                -4.7128390792089085, 
                                2.217463605401367, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "RigidComponent": {
                    "members": {
                        "angularDamping": 1.0, 
                        "angularMass": {
                            "type": "Vector3", 
                            "values": [
                                -1.0, 
                                -1.0, 
                                -1.0
                            ]
                        }, 
                        "centerOfMass": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "collide": true, 
                        "disableGravity": false, 
                        "enableCCD": false, 
                        "enabled": true, 
                        "friction": 0.20000000298023224, 
                        "kinematic": true, 
                        "linearDamping": 0.5, 
                        "mass": 1.0, 
                        "maxContactImpulse": -1.0, 
                        "maxDepenetrationVelocity": -1.0, 
                        "parentRigid": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "positionIterations": 8, 
                        "restitution": 0.10000000149011612, 
                        "sleepThreshold": 4.999999873689376e-06, 
                        "thickness": 0.0, 
                        "velocityIterations": 1
                    }, 
                    "type": "RigidComponent"
                }, 
                "RigidUIComponent": {
                    "members": {
                        "airDensity": 1.0, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "shaded": true, 
                        "shapeIcon": "mesh"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 1
        }, 
        "2": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.5067222118377686, 
                                0.5067222118377686, 
                                0.5067222118377686, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ColorComponent"
                }, 
                "GeometryDescriptionComponent": {
                    "members": {
                        "extents": {
                            "type": "Vector3", 
                            "values": [
                                30.200000762939453, 
                                6.600000381469727, 
                                6.600002288818359
                            ]
                        }, 
                        "length": 23.600000381469727, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                3.5762786865234375e-07, 
                                -5.960464477539062e-07
                            ]
                        }, 
                        "radius": 3.299999952316284, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|environment_grp|pCylinder3", 
                        "shortestPath": "pCylinder3", 
                        "value": "rRigid13"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.5977055048534994, 
                                0.029453084843964195, 
                                -0.8011745410714183, 
                                0.0, 
                                -0.049217198756889825, 
                                0.9987880993216353, 
                                3.469446951953615e-18, 
                                0.0, 
                                0.8002035971016054, 
                                0.03943156662687198, 
                                0.598430743477474, 
                                0.0, 
                                -20.7321220072764, 
                                -4.225989673528756, 
                                -4.795036148906874, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "RigidComponent": {
                    "members": {
                        "angularDamping": 1.0, 
                        "angularMass": {
                            "type": "Vector3", 
                            "values": [
                                -1.0, 
                                -1.0, 
                                -1.0
                            ]
                        }, 
                        "centerOfMass": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "collide": true, 
                        "disableGravity": false, 
                        "enableCCD": false, 
                        "enabled": true, 
                        "friction": 0.20000000298023224, 
                        "kinematic": true, 
                        "linearDamping": 0.5, 
                        "mass": 1.0, 
                        "maxContactImpulse": -1.0, 
                        "maxDepenetrationVelocity": -1.0, 
                        "parentRigid": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "positionIterations": 8, 
                        "restitution": 0.10000000149011612, 
                        "sleepThreshold": 4.999999873689376e-06, 
                        "thickness": 0.0, 
                        "velocityIterations": 1
                    }, 
                    "type": "RigidComponent"
                }, 
                "RigidUIComponent": {
                    "members": {
                        "airDensity": 1.0, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "shaded": true, 
                        "shapeIcon": "mesh"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                0.9999999999999999
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                0.9999999999999999
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 2
        }, 
        "3": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.3815000057220459, 
                                0.3815000057220459, 
                                0.3815000057220459, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ColorComponent"
                }, 
                "GeometryDescriptionComponent": {
                    "members": {
                        "extents": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "length": 1.0, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "radius": 0.5, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "type": "Box"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|environment_grp|pCube1", 
                        "shortestPath": "pCube1", 
                        "value": "rRigid15"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.9987880993216353, 
                                0.04921719875688982, 
                                0.0, 
                                0.0, 
                                -0.04921719875688982, 
                                0.9987880993216353, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                -15.073213759565672, 
                                -2.009941029291662, 
                                0.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "RigidComponent": {
                    "members": {
                        "angularDamping": 1.0, 
                        "angularMass": {
                            "type": "Vector3", 
                            "values": [
                                -1.0, 
                                -1.0, 
                                -1.0
                            ]
                        }, 
                        "centerOfMass": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "collide": true, 
                        "disableGravity": false, 
                        "enableCCD": false, 
                        "enabled": true, 
                        "friction": 0.20000000298023224, 
                        "kinematic": true, 
                        "linearDamping": 0.5, 
                        "mass": 1.0, 
                        "maxContactImpulse": -1.0, 
                        "maxDepenetrationVelocity": -1.0, 
                        "parentRigid": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "positionIterations": 8, 
                        "restitution": 0.10000000149011612, 
                        "sleepThreshold": 4.999999873689376e-06, 
                        "thickness": 0.0, 
                        "velocityIterations": 1
                    }, 
                    "type": "RigidComponent"
                }, 
                "RigidUIComponent": {
                    "members": {
                        "airDensity": 1.0, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "shaded": true, 
                        "shapeIcon": "mesh"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                60.0, 
                                1.0, 
                                30.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                60.0, 
                                1.0, 
                                30.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 3
        }, 
        "4": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.49583330750465393, 
                                0.49583330750465393, 
                                0.49583330750465393, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ColorComponent"
                }, 
                "GeometryDescriptionComponent": {
                    "members": {
                        "extents": {
                            "type": "Vector3", 
                            "values": [
                                16.5, 
                                2.8000001907348633, 
                                2.8000006675720215
                            ]
                        }, 
                        "length": 13.699999809265137, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                1.7881393432617188e-07, 
                                -2.980232238769531e-07
                            ]
                        }, 
                        "radius": 1.399999976158142, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|environment_grp|pCylinder2", 
                        "shortestPath": "pCylinder2", 
                        "value": "rRigid12"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                -0.2691562240626124, 
                                -0.013263189044143382, 
                                -0.9630051998118891, 
                                0.0, 
                                -0.049217198756889624, 
                                0.9987880993216353, 
                                0.0, 
                                0.0, 
                                0.9618381331569683, 
                                0.04739641832305995, 
                                -0.2694828104634206, 
                                0.0, 
                                -17.2933694355328, 
                                -2.78708396636629, 
                                1.6545183433000952, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "RigidComponent": {
                    "members": {
                        "angularDamping": 1.0, 
                        "angularMass": {
                            "type": "Vector3", 
                            "values": [
                                -1.0, 
                                -1.0, 
                                -1.0
                            ]
                        }, 
                        "centerOfMass": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "collide": true, 
                        "disableGravity": false, 
                        "enableCCD": false, 
                        "enabled": true, 
                        "friction": 0.20000000298023224, 
                        "kinematic": true, 
                        "linearDamping": 0.5, 
                        "mass": 1.0, 
                        "maxContactImpulse": -1.0, 
                        "maxDepenetrationVelocity": -1.0, 
                        "parentRigid": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "positionIterations": 8, 
                        "restitution": 0.10000000149011612, 
                        "sleepThreshold": 4.999999873689376e-06, 
                        "thickness": 0.0, 
                        "velocityIterations": 1
                    }, 
                    "type": "RigidComponent"
                }, 
                "RigidUIComponent": {
                    "members": {
                        "airDensity": 1.0, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "shaded": true, 
                        "shapeIcon": "mesh"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                0.9999999999999999
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                0.9999999999999999
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 4
        }, 
        "5": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.3733333349227905, 
                                0.3733333349227905, 
                                0.3733333349227905, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ColorComponent"
                }, 
                "GeometryDescriptionComponent": {
                    "members": {
                        "extents": {
                            "type": "Vector3", 
                            "values": [
                                20.299999237060547, 
                                6.600000381469727, 
                                6.600002288818359
                            ]
                        }, 
                        "length": 13.699999809265137, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                3.5762786865234375e-07, 
                                -5.960464477539062e-07
                            ]
                        }, 
                        "radius": 3.299999952316284, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|environment_grp|pCylinder1", 
                        "shortestPath": "pCylinder1", 
                        "value": "rRigid11"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.1846387769214951, 
                                0.009098429775190882, 
                                -0.9827643362640712, 
                                0.0, 
                                -0.049217198756889825, 
                                0.9987880993216353, 
                                3.469446951953614e-18, 
                                0.0, 
                                0.9815733234982802, 
                                0.04836890766909169, 
                                0.18486281228911272, 
                                0.0, 
                                -11.09756181254792, 
                                -3.7512282457932473, 
                                -2.5388645162729895, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "RigidComponent": {
                    "members": {
                        "angularDamping": 1.0, 
                        "angularMass": {
                            "type": "Vector3", 
                            "values": [
                                -1.0, 
                                -1.0, 
                                -1.0
                            ]
                        }, 
                        "centerOfMass": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "collide": true, 
                        "disableGravity": false, 
                        "enableCCD": false, 
                        "enabled": true, 
                        "friction": 0.20000000298023224, 
                        "kinematic": true, 
                        "linearDamping": 0.5, 
                        "mass": 1.0, 
                        "maxContactImpulse": -1.0, 
                        "maxDepenetrationVelocity": -1.0, 
                        "parentRigid": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "positionIterations": 8, 
                        "restitution": 0.10000000149011612, 
                        "sleepThreshold": 4.999999873689376e-06, 
                        "thickness": 0.0, 
                        "velocityIterations": 1
                    }, 
                    "type": "RigidComponent"
                }, 
                "RigidUIComponent": {
                    "members": {
                        "airDensity": 1.0, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "shaded": true, 
                        "shapeIcon": "mesh"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                0.9999999999999999
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                0.9999999999999999
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 5
        }, 
        "6": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.5121666789054871, 
                                0.5121666789054871, 
                                0.5121666789054871, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ColorComponent"
                }, 
                "GeometryDescriptionComponent": {
                    "members": {
                        "extents": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "length": 1.0, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "radius": 0.5, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "type": "Box"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|environment_grp|pCube2", 
                        "shortestPath": "pCube2", 
                        "value": "rRigid16"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                -52.958480845782745, 
                                -18.2436617676733, 
                                0.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "RigidComponent": {
                    "members": {
                        "angularDamping": 1.0, 
                        "angularMass": {
                            "type": "Vector3", 
                            "values": [
                                -1.0, 
                                -1.0, 
                                -1.0
                            ]
                        }, 
                        "centerOfMass": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "collide": true, 
                        "disableGravity": false, 
                        "enableCCD": false, 
                        "enabled": true, 
                        "friction": 0.20000000298023224, 
                        "kinematic": true, 
                        "linearDamping": 0.5, 
                        "mass": 1.0, 
                        "maxContactImpulse": -1.0, 
                        "maxDepenetrationVelocity": -1.0, 
                        "parentRigid": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "positionIterations": 8, 
                        "restitution": 0.10000000149011612, 
                        "sleepThreshold": 4.999999873689376e-06, 
                        "thickness": 0.0, 
                        "velocityIterations": 1
                    }, 
                    "type": "RigidComponent"
                }, 
                "RigidUIComponent": {
                    "members": {
                        "airDensity": 1.0, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "shaded": true, 
                        "shapeIcon": "mesh"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                51.999999999999986, 
                                5.0, 
                                52.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                51.999999999999986, 
                                5.0, 
                                52.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 6
        }, 
        "7": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.21000000834465027, 
                                0.699999988079071, 
                                0.6673333644866943, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ColorComponent"
                }, 
                "GeometryDescriptionComponent": {
                    "members": {
                        "extents": {
                            "type": "Vector3", 
                            "values": [
                                2.900002956390381, 
                                0.6000422239303589, 
                                4.720004558563232
                            ]
                        }, 
                        "length": 2.900002956390381, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                -2.384185791015625e-06, 
                                3.224611282348633e-05, 
                                -2.19999098777771
                            ]
                        }, 
                        "radius": 1.4500014781951904, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "type": "ConvexHull"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|car_grp|PartFBXASC046536", 
                        "shortestPath": "PartFBXASC046536", 
                        "value": "rRigid9"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                1.4418291442996889e-06, 
                                0.0, 
                                -0.9999999999989605, 
                                0.0, 
                                -0.258828245630953, 
                                -0.9659233609678688, 
                                -3.7318610790482154e-07, 
                                0.0, 
                                -0.9659233609668648, 
                                0.25882824563122203, 
                                -1.3926964530508457e-06, 
                                0.0, 
                                0.06046434599357253, 
                                3.07776331901551, 
                                -0.10000626973631467, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "RigidComponent": {
                    "members": {
                        "angularDamping": 1.0, 
                        "angularMass": {
                            "type": "Vector3", 
                            "values": [
                                -1.0, 
                                -1.0, 
                                -1.0
                            ]
                        }, 
                        "centerOfMass": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "collide": true, 
                        "disableGravity": false, 
                        "enableCCD": false, 
                        "enabled": true, 
                        "friction": 0.800000011920929, 
                        "kinematic": false, 
                        "linearDamping": 0.5, 
                        "mass": 1.0, 
                        "maxContactImpulse": -1.0, 
                        "maxDepenetrationVelocity": -1.0, 
                        "parentRigid": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "positionIterations": 8, 
                        "restitution": 0.10000000149011612, 
                        "sleepThreshold": 4.999999873689376e-06, 
                        "thickness": 0.0, 
                        "velocityIterations": 1
                    }, 
                    "type": "RigidComponent"
                }, 
                "RigidUIComponent": {
                    "members": {
                        "airDensity": 1.0, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "shaded": true, 
                        "shapeIcon": "mesh"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                0.9999999999999999, 
                                0.9999999999999999, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                0.9999999999999999, 
                                0.9999999999999999, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 7
        }, 
        "8": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }
                    }, 
                    "type": "ConstraintUIComponent"
                }, 
                "DriveComponent": {
                    "members": {
                        "acceleration": true, 
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "enabled": false, 
                        "linearDamping": 100.0, 
                        "linearStiffness": 1000.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                1.4418291442996889e-06, 
                                0.0, 
                                -0.9999999999989605, 
                                0.0, 
                                -0.258828245630953, 
                                -0.9659233609678688, 
                                -3.7318610790482154e-07, 
                                0.0, 
                                -0.9659233609668648, 
                                0.25882824563122203, 
                                -1.3926964530508457e-06, 
                                0.0, 
                                -0.9825356540064275, 
                                -1.7851466809844903, 
                                -0.10000626973631467, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": -1.0, 
                        "angularStiffness": -1.0, 
                        "linearDamping": -1.0, 
                        "linearStiffness": -1.0, 
                        "strength": -1.0
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 7
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -1.0, 
                                0.0, 
                                -2.7869999390151105e-15, 
                                0.0, 
                                2.7869999390151105e-15, 
                                0.0, 
                                -1.0, 
                                0.0, 
                                0.0, 
                                -1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 14
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                1.4418291464091126e-06, 
                                -5.551115123125784e-17, 
                                0.9999999999989606, 
                                0.0, 
                                0.9659233609668647, 
                                -0.25882824563122253, 
                                -1.3926964551602696e-06, 
                                0.0, 
                                0.25882824563095347, 
                                0.9659233609678688, 
                                -3.7318610845993305e-07, 
                                0.0, 
                                -0.9825356602668762, 
                                -1.785146713256836, 
                                -0.10000626742839813, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "JointComponent"
                }, 
                "LimitComponent": {
                    "members": {
                        "angularDamping": 10000.0, 
                        "angularStiffness": 1000000.0, 
                        "enabled": true, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "swing1": -0.01745329238474369, 
                        "swing2": -0.01745329238474369, 
                        "twist": 0.7853981852531433, 
                        "x": -1.0, 
                        "y": -1.0, 
                        "z": -1.0
                    }, 
                    "type": "LimitComponent"
                }, 
                "LimitUIComponent": {
                    "members": {
                        "angularDamping": 10000.0, 
                        "angularStiffness": 1000000.0, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "strength": 1.0
                    }, 
                    "type": "LimitUIComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|car_grp|PartFBXASC046536", 
                        "shortestPath": "PartFBXASC046536", 
                        "value": "rHingeConstraint9"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 8
        }, 
        "9": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.21000000834465027, 
                                0.699999988079071, 
                                0.5366666913032532, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ColorComponent"
                }, 
                "GeometryDescriptionComponent": {
                    "members": {
                        "extents": {
                            "type": "Vector3", 
                            "values": [
                                2.432008743286133, 
                                3.0348620414733887, 
                                3.0348687171936035
                            ]
                        }, 
                        "length": 0.6748620271682739, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.8350197792053222, 
                                0.038075268268585205, 
                                0.010658979415893555
                            ]
                        }, 
                        "radius": 1.5560044050216675, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "type": "ConvexHull"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|car_grp|PartFBXASC046344", 
                        "shortestPath": "PartFBXASC046344", 
                        "value": "rRigid7"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.013057781396935919, 
                                -0.0223426435366344, 
                                -0.9996650942314554, 
                                0.0, 
                                -0.7303638682025697, 
                                0.68260805253306, 
                                -0.024796504616627912, 
                                0.0, 
                                0.6829334626222155, 
                                0.7304430524666643, 
                                -0.007404912829522603, 
                                0.0, 
                                -4.546629340210602, 
                                1.7517226538103143, 
                                -1.9645651952499346, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "RigidComponent": {
                    "members": {
                        "angularDamping": 1.0, 
                        "angularMass": {
                            "type": "Vector3", 
                            "values": [
                                -1.0, 
                                -1.0, 
                                -1.0
                            ]
                        }, 
                        "centerOfMass": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "collide": true, 
                        "disableGravity": false, 
                        "enableCCD": false, 
                        "enabled": true, 
                        "friction": 0.800000011920929, 
                        "kinematic": false, 
                        "linearDamping": 0.5, 
                        "mass": 1.0, 
                        "maxContactImpulse": -1.0, 
                        "maxDepenetrationVelocity": -1.0, 
                        "parentRigid": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "positionIterations": 8, 
                        "restitution": 0.10000000149011612, 
                        "sleepThreshold": 4.999999873689376e-06, 
                        "thickness": 0.0, 
                        "velocityIterations": 1
                    }, 
                    "type": "RigidComponent"
                }, 
                "RigidUIComponent": {
                    "members": {
                        "airDensity": 1.0, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "shaded": false, 
                        "shapeIcon": "mesh"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                0.9999999999999999, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                0.9999999999999999, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 9
        }, 
        "10": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }
                    }, 
                    "type": "ConstraintUIComponent"
                }, 
                "DriveComponent": {
                    "members": {
                        "acceleration": true, 
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "enabled": false, 
                        "linearDamping": 100.0, 
                        "linearStiffness": 1000.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                0.013057781396936807, 
                                -0.02234264353663468, 
                                -0.9996650942314556, 
                                0.0, 
                                -0.7303638682025694, 
                                0.6826080525330602, 
                                -0.02479650461662864, 
                                0.0, 
                                0.6829334626222158, 
                                0.730443052466664, 
                                -0.007404912829522159, 
                                0.0, 
                                -5.589629340210602, 
                                -3.111187346189686, 
                                -1.9645651952499346, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": -1.0, 
                        "angularStiffness": -1.0, 
                        "linearDamping": -1.0, 
                        "linearStiffness": -1.0, 
                        "strength": -1.0
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 9
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 14
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                0.013057781396936807, 
                                -0.02234264353663468, 
                                -0.9996650942314556, 
                                0.0, 
                                -0.7303638682025694, 
                                0.6826080525330602, 
                                -0.02479650461662864, 
                                0.0, 
                                0.6829334626222158, 
                                0.730443052466664, 
                                -0.007404912829522159, 
                                0.0, 
                                -5.589629340210602, 
                                -3.111187346189686, 
                                -1.9645651952499346, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "JointComponent"
                }, 
                "LimitComponent": {
                    "members": {
                        "angularDamping": 10000.0, 
                        "angularStiffness": 1000000.0, 
                        "enabled": false, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "swing1": 0.0, 
                        "swing2": 0.0, 
                        "twist": 0.0, 
                        "x": -1.0, 
                        "y": -1.0, 
                        "z": -1.0
                    }, 
                    "type": "LimitComponent"
                }, 
                "LimitUIComponent": {
                    "members": {
                        "angularDamping": -1.0, 
                        "angularStiffness": -1.0, 
                        "linearDamping": -1.0, 
                        "linearStiffness": -1.0, 
                        "strength": -1.0
                    }, 
                    "type": "LimitUIComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|car_grp|PartFBXASC046344", 
                        "shortestPath": "PartFBXASC046344", 
                        "value": "ignoreCollisions"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 10
        }, 
        "11": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 3, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }
                    }, 
                    "type": "ConstraintUIComponent"
                }, 
                "DriveComponent": {
                    "members": {
                        "acceleration": true, 
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "enabled": false, 
                        "linearDamping": 100.0, 
                        "linearStiffness": 1000.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                -8.295428478799494e-06, 
                                0.9999999999571783, 
                                4.102397482164123e-06, 
                                0.0, 
                                -0.8352815346999176, 
                                -4.673427880019787e-06, 
                                -0.5498224784123595, 
                                0.0, 
                                -0.5498224783696428, 
                                -7.987669910503039e-06, 
                                0.8352815347029173, 
                                0.0, 
                                0.3200827395668058, 
                                0.4987219895099251, 
                                0.8115559194402984, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": -1.0, 
                        "angularStiffness": -1.0, 
                        "linearDamping": -1.0, 
                        "linearStiffness": -1.0, 
                        "strength": -1.0
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 9
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -1.0, 
                                0.0, 
                                -1.8988215193149856e-15, 
                                0.0, 
                                1.8988215193149856e-15, 
                                0.0, 
                                -1.0, 
                                0.0, 
                                0.0, 
                                -1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 15
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                8.295428477467226e-06, 
                                -0.9999999999571781, 
                                -4.102397482386166e-06, 
                                0.0, 
                                0.5498224783696423, 
                                7.987669909947925e-06, 
                                -0.8352815347029177, 
                                0.0, 
                                0.835281534699918, 
                                4.673427878576497e-06, 
                                0.5498224784123589, 
                                0.0, 
                                0.32008275389671326, 
                                0.49872198700904846, 
                                0.8115559220314026, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "JointComponent"
                }, 
                "LimitComponent": {
                    "members": {
                        "angularDamping": 10000.0, 
                        "angularStiffness": 1000000.0, 
                        "enabled": true, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "swing1": -0.01745329238474369, 
                        "swing2": -0.01745329238474369, 
                        "twist": 0.0, 
                        "x": -1.0, 
                        "y": -1.0, 
                        "z": -1.0
                    }, 
                    "type": "LimitComponent"
                }, 
                "LimitUIComponent": {
                    "members": {
                        "angularDamping": 10000.0, 
                        "angularStiffness": 1000000.0, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "strength": 1.0
                    }, 
                    "type": "LimitUIComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|car_grp|PartFBXASC046344", 
                        "shortestPath": "PartFBXASC046344", 
                        "value": "rHingeConstraint7"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 11
        }, 
        "12": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.21000000834465027, 
                                0.45499998331069946, 
                                0.699999988079071, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ColorComponent"
                }, 
                "GeometryDescriptionComponent": {
                    "members": {
                        "extents": {
                            "type": "Vector3", 
                            "values": [
                                1.649985909461975, 
                                0.792012095451355, 
                                3.1400132179260254
                            ]
                        }, 
                        "length": 2.799985885620117, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.07400083541870117, 
                                7.212162017822266e-06, 
                                1.200000524520874
                            ]
                        }, 
                        "radius": 1.3999929428100586, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "type": "Box"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|car_grp|PartFBXASC046332", 
                        "shortestPath": "PartFBXASC046332", 
                        "value": "rRigid4"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.23456717542121308, 
                                -0.9717837257916426, 
                                0.024791742605702105, 
                                0.0, 
                                0.013055739652171272, 
                                -0.022351668193173246, 
                                -0.9996649191559726, 
                                0.0, 
                                0.9720122364852455, 
                                0.2348122509910755, 
                                0.007444387648127826, 
                                0.0, 
                                -5.417064666748047, 
                                1.883369768138352, 
                                1.28001070022583, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "RigidComponent": {
                    "members": {
                        "angularDamping": 1.0, 
                        "angularMass": {
                            "type": "Vector3", 
                            "values": [
                                -1.0, 
                                -1.0, 
                                -1.0
                            ]
                        }, 
                        "centerOfMass": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "collide": false, 
                        "disableGravity": false, 
                        "enableCCD": false, 
                        "enabled": true, 
                        "friction": 0.800000011920929, 
                        "kinematic": false, 
                        "linearDamping": 0.5, 
                        "mass": 1.0, 
                        "maxContactImpulse": -1.0, 
                        "maxDepenetrationVelocity": -1.0, 
                        "parentRigid": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "positionIterations": 8, 
                        "restitution": 0.10000000149011612, 
                        "sleepThreshold": 4.999999873689376e-06, 
                        "thickness": 0.0, 
                        "velocityIterations": 1
                    }, 
                    "type": "RigidComponent"
                }, 
                "RigidUIComponent": {
                    "members": {
                        "airDensity": 1.0, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "shaded": false, 
                        "shapeIcon": "mesh"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 12
        }, 
        "13": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }
                    }, 
                    "type": "ConstraintUIComponent"
                }, 
                "DriveComponent": {
                    "members": {
                        "acceleration": true, 
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "enabled": false, 
                        "linearDamping": 100.0, 
                        "linearStiffness": 1000.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                0.23456717542121308, 
                                -0.9717837257916426, 
                                0.024791742605702105, 
                                0.0, 
                                0.013055739652171272, 
                                -0.022351668193173024, 
                                -0.9996649191559726, 
                                0.0, 
                                0.9720122364852453, 
                                0.23481225099107556, 
                                0.007444387648127937, 
                                0.0, 
                                -6.460064666748047, 
                                -2.979540231861648, 
                                1.28001070022583, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": -1.0, 
                        "angularStiffness": -1.0, 
                        "linearDamping": -1.0, 
                        "linearStiffness": -1.0, 
                        "strength": -1.0
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 12
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                0.99953349149798, 
                                0.0, 
                                -0.03054176441952214, 
                                0.0, 
                                0.03054176441952214, 
                                -8.659739592076221e-15, 
                                0.99953349149798, 
                                0.0, 
                                -2.6367796834847473e-16, 
                                -1.0, 
                                -8.659739592076221e-15, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 14
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                0.20477077909997587, 
                                -0.9785019608740199, 
                                0.02455281231320009, 
                                0.0, 
                                0.9787228799251214, 
                                0.20502271945977268, 
                                0.008198098340210415, 
                                0.0, 
                                -0.013055739652171612, 
                                0.022351668193173066, 
                                0.9996649191559724, 
                                0.0, 
                                -6.460064888000488, 
                                -2.9795403480529785, 
                                1.28001070022583, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "JointComponent"
                }, 
                "LimitComponent": {
                    "members": {
                        "angularDamping": 10000.0, 
                        "angularStiffness": 1000000.0, 
                        "enabled": true, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "swing1": -0.01745329238474369, 
                        "swing2": -0.01745329238474369, 
                        "twist": 0.7853981852531433, 
                        "x": -1.0, 
                        "y": -1.0, 
                        "z": -1.0
                    }, 
                    "type": "LimitComponent"
                }, 
                "LimitUIComponent": {
                    "members": {
                        "angularDamping": 10000.0, 
                        "angularStiffness": 1000000.0, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "strength": 1.0
                    }, 
                    "type": "LimitUIComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|car_grp|PartFBXASC046332", 
                        "shortestPath": "PartFBXASC046332", 
                        "value": "rHingeConstraint3"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 13
        }, 
        "14": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.21000000834465027, 
                                0.699999988079071, 
                                0.49583327770233154, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ColorComponent"
                }, 
                "GeometryDescriptionComponent": {
                    "members": {
                        "extents": {
                            "type": "Vector3", 
                            "values": [
                                15.176656723022461, 
                                3.3046021461486816, 
                                5.4301018714904785
                            ]
                        }, 
                        "length": 16.846656799316406, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                -1.02111698251382, 
                                0.953178100622818, 
                                -0.10005593299865727
                            ]
                        }, 
                        "radius": 8.423328399658203, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.14072049463443376, 
                                0.9900493636126637
                            ]
                        }, 
                        "type": "Box"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|car_grp|PartFBXASC046515", 
                        "shortestPath": "PartFBXASC046515", 
                        "value": "rRigid"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                1.043, 
                                4.86291, 
                                0.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "RigidComponent": {
                    "members": {
                        "angularDamping": 1.0, 
                        "angularMass": {
                            "type": "Vector3", 
                            "values": [
                                -1.0, 
                                -1.0, 
                                -1.0
                            ]
                        }, 
                        "centerOfMass": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "collide": true, 
                        "disableGravity": false, 
                        "enableCCD": false, 
                        "enabled": true, 
                        "friction": 0.800000011920929, 
                        "kinematic": false, 
                        "linearDamping": 0.5, 
                        "mass": 5.0, 
                        "maxContactImpulse": -1.0, 
                        "maxDepenetrationVelocity": -1.0, 
                        "parentRigid": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "positionIterations": 8, 
                        "restitution": 0.10000000149011612, 
                        "sleepThreshold": 4.999999873689376e-06, 
                        "thickness": 0.0, 
                        "velocityIterations": 1
                    }, 
                    "type": "RigidComponent"
                }, 
                "RigidUIComponent": {
                    "members": {
                        "airDensity": 1.0, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "shaded": false, 
                        "shapeIcon": "mesh"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 14
        }, 
        "15": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.21000000834465027, 
                                0.4386666715145111, 
                                0.699999988079071, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ColorComponent"
                }, 
                "GeometryDescriptionComponent": {
                    "members": {
                        "extents": {
                            "type": "Vector3", 
                            "values": [
                                1.649985909461975, 
                                0.792012095451355, 
                                3.1400132179260254
                            ]
                        }, 
                        "length": 2.799985885620117, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.07400083541870117, 
                                7.212162017822266e-06, 
                                1.200000524520874
                            ]
                        }, 
                        "radius": 1.3999929428100586, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "type": "Box"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|car_grp|PartFBXASC046563", 
                        "shortestPath": "PartFBXASC046563", 
                        "value": "rRigid5"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.23456717542121308, 
                                -0.9717837257916426, 
                                0.024791742605702105, 
                                0.0, 
                                0.013055739652171272, 
                                -0.022351668193173246, 
                                -0.9996649191559726, 
                                0.0, 
                                0.9720122364852455, 
                                0.2348122509910755, 
                                0.007444387648127826, 
                                0.0, 
                                -5.4170637130737305, 
                                1.883357847209397, 
                                -1.4799872636795044, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "RigidComponent": {
                    "members": {
                        "angularDamping": 1.0, 
                        "angularMass": {
                            "type": "Vector3", 
                            "values": [
                                -1.0, 
                                -1.0, 
                                -1.0
                            ]
                        }, 
                        "centerOfMass": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "collide": false, 
                        "disableGravity": false, 
                        "enableCCD": false, 
                        "enabled": true, 
                        "friction": 0.800000011920929, 
                        "kinematic": false, 
                        "linearDamping": 0.5, 
                        "mass": 1.0, 
                        "maxContactImpulse": -1.0, 
                        "maxDepenetrationVelocity": -1.0, 
                        "parentRigid": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "positionIterations": 8, 
                        "restitution": 0.10000000149011612, 
                        "sleepThreshold": 4.999999873689376e-06, 
                        "thickness": 0.0, 
                        "velocityIterations": 1
                    }, 
                    "type": "RigidComponent"
                }, 
                "RigidUIComponent": {
                    "members": {
                        "airDensity": 1.0, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "shaded": false, 
                        "shapeIcon": "mesh"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 15
        }, 
        "16": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }
                    }, 
                    "type": "ConstraintUIComponent"
                }, 
                "DriveComponent": {
                    "members": {
                        "acceleration": true, 
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "enabled": false, 
                        "linearDamping": 100.0, 
                        "linearStiffness": 1000.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                0.2345671754212132, 
                                -0.9717837257916426, 
                                0.024791742605702105, 
                                0.0, 
                                0.01305573965217105, 
                                -0.022351668193173246, 
                                -0.9996649191559726, 
                                0.0, 
                                0.9720122364852455, 
                                0.23481225099107567, 
                                0.007444387648127604, 
                                0.0, 
                                -6.460063713073731, 
                                -2.9795521527906033, 
                                -1.4799872636795044, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": -1.0, 
                        "angularStiffness": -1.0, 
                        "linearDamping": -1.0, 
                        "linearStiffness": -1.0, 
                        "strength": -1.0
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 15
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                -1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 14
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                0.23456717542120464, 
                                -0.9717837257916445, 
                                0.02479174260570214, 
                                0.0, 
                                0.9720122364852474, 
                                0.23481225099106706, 
                                0.007444387648127856, 
                                0.0, 
                                -0.013055739652171045, 
                                0.022351668193173285, 
                                0.9996649191559724, 
                                0.0, 
                                -6.460063934326172, 
                                -2.9795522689819336, 
                                -1.4799872636795044, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "JointComponent"
                }, 
                "LimitComponent": {
                    "members": {
                        "angularDamping": 10000.0, 
                        "angularStiffness": 1000000.0, 
                        "enabled": true, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "swing1": -0.01745329238474369, 
                        "swing2": -0.01745329238474369, 
                        "twist": 0.7853981852531433, 
                        "x": -1.0, 
                        "y": -1.0, 
                        "z": -1.0
                    }, 
                    "type": "LimitComponent"
                }, 
                "LimitUIComponent": {
                    "members": {
                        "angularDamping": 10000.0, 
                        "angularStiffness": 1000000.0, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "strength": 1.0
                    }, 
                    "type": "LimitUIComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|car_grp|PartFBXASC046563", 
                        "shortestPath": "PartFBXASC046563", 
                        "value": "rHingeConstraint4"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 16
        }, 
        "17": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.21000000834465027, 
                                0.5774999856948853, 
                                0.699999988079071, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ColorComponent"
                }, 
                "GeometryDescriptionComponent": {
                    "members": {
                        "extents": {
                            "type": "Vector3", 
                            "values": [
                                3.5522005558013916, 
                                0.7400078773498535, 
                                2.339996814727783
                            ]
                        }, 
                        "length": 3.5522005558013916, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                -1.1920928955078125e-07, 
                                -4.5299530029296875e-06, 
                                0.8000016212463379
                            ]
                        }, 
                        "radius": 1.7761002779006958, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "type": "Box"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|car_grp|PartFBXASC046322", 
                        "shortestPath": "PartFBXASC046322", 
                        "value": "rRigid1"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                1.3349124028394499e-08, 
                                0.0, 
                                1.0, 
                                0.0, 
                                -0.36665297999437957, 
                                -0.9303577764823814, 
                                4.894496113960755e-09, 
                                0.0, 
                                0.9303577764823815, 
                                -0.36665297999437957, 
                                -1.2419461237200835e-08, 
                                0.0, 
                                3.7533330917358434, 
                                4.7505002021789755, 
                                -0.10001200437545776, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "RigidComponent": {
                    "members": {
                        "angularDamping": 1.0, 
                        "angularMass": {
                            "type": "Vector3", 
                            "values": [
                                -1.0, 
                                -1.0, 
                                -1.0
                            ]
                        }, 
                        "centerOfMass": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "collide": true, 
                        "disableGravity": false, 
                        "enableCCD": false, 
                        "enabled": true, 
                        "friction": 0.800000011920929, 
                        "kinematic": false, 
                        "linearDamping": 0.5, 
                        "mass": 1.0, 
                        "maxContactImpulse": -1.0, 
                        "maxDepenetrationVelocity": -1.0, 
                        "parentRigid": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "positionIterations": 8, 
                        "restitution": 0.10000000149011612, 
                        "sleepThreshold": 4.999999873689376e-06, 
                        "thickness": 0.0, 
                        "velocityIterations": 1
                    }, 
                    "type": "RigidComponent"
                }, 
                "RigidUIComponent": {
                    "members": {
                        "airDensity": 1.0, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "shaded": false, 
                        "shapeIcon": "mesh"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                0.9999999999999998, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                0.9999999999999998, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 17
        }, 
        "18": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }
                    }, 
                    "type": "ConstraintUIComponent"
                }, 
                "DriveComponent": {
                    "members": {
                        "acceleration": true, 
                        "angularDamping": 20.0, 
                        "angularStiffness": 4000.0, 
                        "enabled": true, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                1.3349124028394499e-08, 
                                0.0, 
                                1.0, 
                                0.0, 
                                -0.36665297999437957, 
                                -0.9303577764823814, 
                                4.894496113960755e-09, 
                                0.0, 
                                0.9303577764823815, 
                                -0.36665297999437957, 
                                -1.2419461237200835e-08, 
                                0.0, 
                                2.7103330917358432, 
                                -0.11240979782102478, 
                                -0.10001200437545776, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": 20.0, 
                        "angularStiffness": 4000.0, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "strength": 1.0
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 17
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                -1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 14
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                4.894496807850146e-09, 
                                5.551115123125784e-17, 
                                1.0000000000000002, 
                                0.0, 
                                0.9303577764823823, 
                                -0.3666529799943783, 
                                -4.553633192738716e-09, 
                                0.0, 
                                0.3666529799943782, 
                                0.9303577764823823, 
                                -1.7945820385278921e-09, 
                                0.0, 
                                2.7103331089019775, 
                                -0.1124098002910614, 
                                -0.10001200437545776, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "JointComponent"
                }, 
                "LimitComponent": {
                    "members": {
                        "angularDamping": 10000.0, 
                        "angularStiffness": 1000000.0, 
                        "enabled": true, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "swing1": -0.01745329238474369, 
                        "swing2": -0.01745329238474369, 
                        "twist": 0.617398202419281, 
                        "x": -1.0, 
                        "y": -1.0, 
                        "z": -1.0
                    }, 
                    "type": "LimitComponent"
                }, 
                "LimitUIComponent": {
                    "members": {
                        "angularDamping": 10000.0, 
                        "angularStiffness": 1000000.0, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "strength": 1.0
                    }, 
                    "type": "LimitUIComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|car_grp|PartFBXASC046322", 
                        "shortestPath": "PartFBXASC046322", 
                        "value": "rHingeConstraint"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 18
        }, 
        "19": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.21000000834465027, 
                                0.699999988079071, 
                                0.43050000071525574, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ColorComponent"
                }, 
                "GeometryDescriptionComponent": {
                    "members": {
                        "extents": {
                            "type": "Vector3", 
                            "values": [
                                0.8300058841705322, 
                                0.7400037050247192, 
                                3.5000007152557373
                            ]
                        }, 
                        "length": 0.8300058841705322, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                3.4570693969726562e-06, 
                                5.960464477539063e-08, 
                                -1.1920928955078125e-07
                            ]
                        }, 
                        "radius": 0.4150029420852661, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "type": "Box"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|car_grp|PartFBXASC046555", 
                        "shortestPath": "PartFBXASC046555", 
                        "value": "rRigid6"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.2588302364574099, 
                                -0.9659228275050764, 
                                1.6543612251060557e-24, 
                                0.0, 
                                -0.965922827505076, 
                                -0.25883023645741, 
                                -2.6698248623342893e-08, 
                                0.0, 
                                2.5788447799692877e-08, 
                                6.910314004178557e-09, 
                                -1.0, 
                                0.0, 
                                -2.8577861724201052, 
                                1.5599937085701439, 
                                -0.06978520012199718, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "RigidComponent": {
                    "members": {
                        "angularDamping": 1.0, 
                        "angularMass": {
                            "type": "Vector3", 
                            "values": [
                                -1.0, 
                                -1.0, 
                                -1.0
                            ]
                        }, 
                        "centerOfMass": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "collide": false, 
                        "disableGravity": false, 
                        "enableCCD": false, 
                        "enabled": true, 
                        "friction": 0.800000011920929, 
                        "kinematic": false, 
                        "linearDamping": 0.5, 
                        "mass": 1.0, 
                        "maxContactImpulse": -1.0, 
                        "maxDepenetrationVelocity": -1.0, 
                        "parentRigid": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "positionIterations": 8, 
                        "restitution": 0.10000000149011612, 
                        "sleepThreshold": 4.999999873689376e-06, 
                        "thickness": 0.0, 
                        "velocityIterations": 1
                    }, 
                    "type": "RigidComponent"
                }, 
                "RigidUIComponent": {
                    "members": {
                        "airDensity": 1.0, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "shaded": false, 
                        "shapeIcon": "mesh"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0000000000000002
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0000000000000002
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 19
        }, 
        "20": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }
                    }, 
                    "type": "ConstraintUIComponent"
                }, 
                "DriveComponent": {
                    "members": {
                        "acceleration": true, 
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "enabled": false, 
                        "linearDamping": 100.0, 
                        "linearStiffness": 1000.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                0.9993811616195004, 
                                0.024969206721902906, 
                                0.02477564359884062, 
                                0.0, 
                                0.024953221547480163, 
                                -0.00682552270703618, 
                                -0.9996653184812296, 
                                0.0, 
                                -0.0247917432719094, 
                                0.9996649193382023, 
                                -0.007444360958814622, 
                                0.0, 
                                0.949523877846076, 
                                -1.3690885426589423, 
                                2.4222173156168276, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": -1.0, 
                        "angularStiffness": -1.0, 
                        "linearDamping": -1.0, 
                        "linearStiffness": -1.0, 
                        "strength": -1.0
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 19
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -1.0, 
                                0.0, 
                                -1.8988215193149856e-15, 
                                0.0, 
                                1.8988215193149856e-15, 
                                0.0, 
                                -1.0, 
                                0.0, 
                                0.0, 
                                -1.0, 
                                0.0, 
                                0.0, 
                                8.107810331261279e-18, 
                                -1.4424360177499334e-16, 
                                1.365785164217608, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 15
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -0.9993811616195007, 
                                -0.024969206721902133, 
                                -0.024775643598840498, 
                                0.0, 
                                0.02479174327190863, 
                                -0.9996649193382026, 
                                0.007444360958814643, 
                                0.0, 
                                -0.024953221547480038, 
                                0.0068255227070362755, 
                                0.9996653184812295, 
                                0.0, 
                                0.9156636710207393, 
                                -0.003761014519557986, 
                                2.412049971324961, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "JointComponent"
                }, 
                "LimitComponent": {
                    "members": {
                        "angularDamping": 10000.0, 
                        "angularStiffness": 1000000.0, 
                        "enabled": true, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "swing1": -0.01745329238474369, 
                        "swing2": -0.01745329238474369, 
                        "twist": 0.7853981852531433, 
                        "x": -1.0, 
                        "y": -1.0, 
                        "z": -1.0
                    }, 
                    "type": "LimitComponent"
                }, 
                "LimitUIComponent": {
                    "members": {
                        "angularDamping": 10000.0, 
                        "angularStiffness": 1000000.0, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "strength": 1.0
                    }, 
                    "type": "LimitUIComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|car_grp|PartFBXASC046555", 
                        "shortestPath": "PartFBXASC046555", 
                        "value": "rHingeConstraint5"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 20
        }, 
        "21": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 3, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }
                    }, 
                    "type": "ConstraintUIComponent"
                }, 
                "DriveComponent": {
                    "members": {
                        "acceleration": true, 
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "enabled": false, 
                        "linearDamping": 100.0, 
                        "linearStiffness": 1000.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                0.9993811616195004, 
                                0.024969206721902913, 
                                0.024775643598840512, 
                                0.0, 
                                0.024953221547480052, 
                                -0.00682552270703618, 
                                -0.9996653184812296, 
                                0.0, 
                                -0.02479174327190941, 
                                0.9996649193382023, 
                                -0.007444360958814622, 
                                0.0, 
                                0.8811105269981181, 
                                1.3899848777027044, 
                                2.4016689486684157, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": -1.0, 
                        "angularStiffness": -1.0, 
                        "linearDamping": -1.0, 
                        "linearStiffness": -1.0, 
                        "strength": -1.0
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 19
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                -1.0, 
                                0.0, 
                                0.0, 
                                -8.654596182045089e-17, 
                                4.3815154947335877e-16, 
                                -1.3800000896599232, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 12
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                0.9993811616195005, 
                                0.024969206721902712, 
                                0.024775643598840442, 
                                0.0, 
                                -0.024791743271909215, 
                                0.9996649193382023, 
                                -0.007444360958814531, 
                                0.0, 
                                -0.024953221547479983, 
                                0.0068255227070361515, 
                                0.9996653184812295, 
                                0.0, 
                                0.9153231569111445, 
                                0.010447167798513375, 
                                2.4119422442117666, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "JointComponent"
                }, 
                "LimitComponent": {
                    "members": {
                        "angularDamping": 10000.0, 
                        "angularStiffness": 1000000.0, 
                        "enabled": true, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "swing1": -0.01745329238474369, 
                        "swing2": -0.01745329238474369, 
                        "twist": 0.7853981852531433, 
                        "x": -1.0, 
                        "y": -1.0, 
                        "z": -1.0
                    }, 
                    "type": "LimitComponent"
                }, 
                "LimitUIComponent": {
                    "members": {
                        "angularDamping": 10000.0, 
                        "angularStiffness": 1000000.0, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "strength": 1.0
                    }, 
                    "type": "LimitUIComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|car_grp|PartFBXASC046555", 
                        "shortestPath": "PartFBXASC046555", 
                        "value": "rHingeConstraint6"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 21
        }, 
        "22": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 4, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }
                    }, 
                    "type": "ConstraintUIComponent"
                }, 
                "DriveComponent": {
                    "members": {
                        "acceleration": true, 
                        "angularDamping": 0.0, 
                        "angularStiffness": 0.0, 
                        "enabled": true, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 100000.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                0.25877434097220275, 
                                -0.9659378023725601, 
                                -4.9010928941945766e-05, 
                                0.0, 
                                -0.9659378033060247, 
                                -0.2587743418413919, 
                                1.2201889237936778e-05, 
                                0.0, 
                                -2.446903695527328e-05, 
                                4.418397319400786e-05, 
                                -0.9999999987245216, 
                                0.0, 
                                -3.900779799274945, 
                                -3.3030197043696905, 
                                -0.07482590976623499, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": 0.0, 
                        "angularStiffness": 0.0, 
                        "linearDamping": 100.0, 
                        "linearStiffness": 1000.0, 
                        "strength": 10.0
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 19
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 14
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                0.2588302364574099, 
                                -0.9659228275050764, 
                                1.6543612251060557e-24, 
                                0.0, 
                                -0.965922827505076, 
                                -0.25883023645741, 
                                -2.6698248623342893e-08, 
                                0.0, 
                                2.5788447799692877e-08, 
                                6.910314004178557e-09, 
                                -1.0, 
                                0.0, 
                                -3.9007861724201054, 
                                -3.3029162914298564, 
                                -0.06978520012199718, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "JointComponent"
                }, 
                "LimitComponent": {
                    "members": {
                        "angularDamping": 10000.0, 
                        "angularStiffness": 1000000.0, 
                        "enabled": false, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "swing1": 0.0, 
                        "swing2": 0.0, 
                        "twist": 0.0, 
                        "x": -1.0, 
                        "y": -1.0, 
                        "z": -1.0
                    }, 
                    "type": "LimitComponent"
                }, 
                "LimitUIComponent": {
                    "members": {
                        "angularDamping": -1.0, 
                        "angularStiffness": -1.0, 
                        "linearDamping": -1.0, 
                        "linearStiffness": -1.0, 
                        "strength": -1.0
                    }, 
                    "type": "LimitUIComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|car_grp|PartFBXASC046555", 
                        "shortestPath": "PartFBXASC046555", 
                        "value": "rPointConstraint"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 22
        }, 
        "23": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.21000000834465027, 
                                0.699999988079071, 
                                0.3569999933242798, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ColorComponent"
                }, 
                "GeometryDescriptionComponent": {
                    "members": {
                        "extents": {
                            "type": "Vector3", 
                            "values": [
                                2.432008743286133, 
                                3.0348620414733887, 
                                3.0348687171936035
                            ]
                        }, 
                        "length": 3.0348620414733887, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.38501977920532227, 
                                0.038075268268585205, 
                                -0.010658979415893555
                            ]
                        }, 
                        "radius": 1.2160043716430664, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "type": "ConvexHull"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|car_grp|PartFBXASC046565", 
                        "shortestPath": "PartFBXASC046565", 
                        "value": "rRigid8"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.013057781396935919, 
                                -0.0223426435366344, 
                                0.9996650942314554, 
                                0.0, 
                                -0.7303638682025697, 
                                0.68260805253306, 
                                0.024796504616627912, 
                                0.0, 
                                -0.6829334626222155, 
                                -0.7304430524666643, 
                                -0.007404912829522603, 
                                0.0, 
                                -4.546629340210602, 
                                1.7517226538103143, 
                                1.8370517118698213, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "RigidComponent": {
                    "members": {
                        "angularDamping": 1.0, 
                        "angularMass": {
                            "type": "Vector3", 
                            "values": [
                                -1.0, 
                                -1.0, 
                                -1.0
                            ]
                        }, 
                        "centerOfMass": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "collide": true, 
                        "disableGravity": false, 
                        "enableCCD": false, 
                        "enabled": true, 
                        "friction": 0.800000011920929, 
                        "kinematic": false, 
                        "linearDamping": 0.5, 
                        "mass": 1.0, 
                        "maxContactImpulse": -1.0, 
                        "maxDepenetrationVelocity": -1.0, 
                        "parentRigid": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "positionIterations": 8, 
                        "restitution": 0.10000000149011612, 
                        "sleepThreshold": 4.999999873689376e-06, 
                        "thickness": 0.0, 
                        "velocityIterations": 1
                    }, 
                    "type": "RigidComponent"
                }, 
                "RigidUIComponent": {
                    "members": {
                        "airDensity": 1.0, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "shaded": false, 
                        "shapeIcon": "mesh"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                0.9999999999999999, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                0.9999999999999999, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 23
        }, 
        "24": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }
                    }, 
                    "type": "ConstraintUIComponent"
                }, 
                "DriveComponent": {
                    "members": {
                        "acceleration": true, 
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "enabled": false, 
                        "linearDamping": 100.0, 
                        "linearStiffness": 1000.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                0.013057781396936474, 
                                -0.022342643536634902, 
                                0.9996650942314553, 
                                0.0, 
                                -0.7303638682025687, 
                                0.6826080525330609, 
                                0.02479650461662864, 
                                0.0, 
                                -0.6829334626222164, 
                                -0.7304430524666633, 
                                -0.007404912829522603, 
                                0.0, 
                                -5.589629340210602, 
                                -3.111187346189686, 
                                1.8370517118698213, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": -1.0, 
                        "angularStiffness": -1.0, 
                        "linearDamping": -1.0, 
                        "linearStiffness": -1.0, 
                        "strength": -1.0
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 23
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 14
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                0.013057781396936474, 
                                -0.022342643536634902, 
                                0.9996650942314553, 
                                0.0, 
                                -0.7303638682025687, 
                                0.6826080525330609, 
                                0.02479650461662864, 
                                0.0, 
                                -0.6829334626222164, 
                                -0.7304430524666633, 
                                -0.007404912829522603, 
                                0.0, 
                                -5.589629340210602, 
                                -3.111187346189686, 
                                1.8370517118698213, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "JointComponent"
                }, 
                "LimitComponent": {
                    "members": {
                        "angularDamping": 10000.0, 
                        "angularStiffness": 1000000.0, 
                        "enabled": false, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "swing1": 0.0, 
                        "swing2": 0.0, 
                        "twist": 0.0, 
                        "x": -1.0, 
                        "y": -1.0, 
                        "z": -1.0
                    }, 
                    "type": "LimitComponent"
                }, 
                "LimitUIComponent": {
                    "members": {
                        "angularDamping": -1.0, 
                        "angularStiffness": -1.0, 
                        "linearDamping": -1.0, 
                        "linearStiffness": -1.0, 
                        "strength": -1.0
                    }, 
                    "type": "LimitUIComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|car_grp|PartFBXASC046565", 
                        "shortestPath": "PartFBXASC046565", 
                        "value": "ignoreCollisions2"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 24
        }, 
        "25": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 3, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }
                    }, 
                    "type": "ConstraintUIComponent"
                }, 
                "DriveComponent": {
                    "members": {
                        "acceleration": true, 
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "enabled": false, 
                        "linearDamping": 100.0, 
                        "linearStiffness": 1000.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                0.049558583987704075, 
                                -0.9986602512586928, 
                                0.014887891357004801, 
                                0.0, 
                                -0.8340520375799658, 
                                -0.049581064993745594, 
                                -0.5494532888269874, 
                                0.0, 
                                0.5494553169838658, 
                                0.014812850840073444, 
                                -0.8353917847861259, 
                                0.0, 
                                0.3459180965656463, 
                                -0.542547648246277, 
                                0.8193082624381645, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": -1.0, 
                        "angularStiffness": -1.0, 
                        "linearDamping": -1.0, 
                        "linearStiffness": -1.0, 
                        "strength": -1.0
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 23
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                -1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 12
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                0.04955858398770285, 
                                -0.998660251258693, 
                                0.014887891357005245, 
                                0.0, 
                                0.5494553169838655, 
                                0.014812850840072445, 
                                -0.8353917847861263, 
                                0.0, 
                                0.8340520375799665, 
                                0.04958106499374498, 
                                0.549453288826987, 
                                0.0, 
                                0.34591808915138245, 
                                -0.5425476431846619, 
                                0.8193082809448242, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "JointComponent"
                }, 
                "LimitComponent": {
                    "members": {
                        "angularDamping": 10000.0, 
                        "angularStiffness": 1000000.0, 
                        "enabled": true, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "swing1": -0.01745329238474369, 
                        "swing2": -0.01745329238474369, 
                        "twist": 0.0, 
                        "x": -1.0, 
                        "y": -1.0, 
                        "z": -1.0
                    }, 
                    "type": "LimitComponent"
                }, 
                "LimitUIComponent": {
                    "members": {
                        "angularDamping": 10000.0, 
                        "angularStiffness": 1000000.0, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "strength": 1.0
                    }, 
                    "type": "LimitUIComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|car_grp|PartFBXASC046565", 
                        "shortestPath": "PartFBXASC046565", 
                        "value": "rHingeConstraint8"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 25
        }, 
        "26": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.699999988079071, 
                                0.3569999933242798, 
                                0.21000000834465027, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ColorComponent"
                }, 
                "GeometryDescriptionComponent": {
                    "members": {
                        "extents": {
                            "type": "Vector3", 
                            "values": [
                                2.396000385284424, 
                                3.138828754425049, 
                                0.8074544668197632
                            ]
                        }, 
                        "length": 3.138828754425049, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                -2.4557113647460938e-05, 
                                1.1995494365692139, 
                                0.03386346995830536
                            ]
                        }, 
                        "radius": 1.198000192642212, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "type": "Box"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|car_grp|polySurface48", 
                        "shortestPath": "polySurface48", 
                        "value": "rRigid2"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                -4.952224109233683e-06, 
                                -9.016928595312333e-06, 
                                -0.9999999999470853, 
                                0.0, 
                                0.3666323263686911, 
                                0.9303659157328078, 
                                -1.020468847606759e-05, 
                                0.0, 
                                0.9303659157755927, 
                                -0.36663232639982674, 
                                -1.3014830106961028e-06, 
                                0.0, 
                                4.3105149269104, 
                                1.9389123916625977, 
                                -0.10001003742218018, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "RigidComponent": {
                    "members": {
                        "angularDamping": 1.0, 
                        "angularMass": {
                            "type": "Vector3", 
                            "values": [
                                -1.0, 
                                -1.0, 
                                -1.0
                            ]
                        }, 
                        "centerOfMass": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "collide": true, 
                        "disableGravity": false, 
                        "enableCCD": false, 
                        "enabled": true, 
                        "friction": 0.800000011920929, 
                        "kinematic": false, 
                        "linearDamping": 0.5, 
                        "mass": 1.0, 
                        "maxContactImpulse": -1.0, 
                        "maxDepenetrationVelocity": -1.0, 
                        "parentRigid": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "positionIterations": 8, 
                        "restitution": 0.10000000149011612, 
                        "sleepThreshold": 4.999999873689376e-06, 
                        "thickness": 0.0, 
                        "velocityIterations": 1
                    }, 
                    "type": "RigidComponent"
                }, 
                "RigidUIComponent": {
                    "members": {
                        "airDensity": 1.0, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "shaded": false, 
                        "shapeIcon": "mesh"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 26
        }, 
        "27": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }
                    }, 
                    "type": "ConstraintUIComponent"
                }, 
                "DriveComponent": {
                    "members": {
                        "acceleration": true, 
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "enabled": false, 
                        "linearDamping": 100.0, 
                        "linearStiffness": 1000.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                -0.9999999999471516, 
                                1.0199822869809001e-05, 
                                -1.2888370096013097e-06, 
                                0.0, 
                                -1.0199794255725524e-05, 
                                -0.9999999997015727, 
                                -2.2199532139050776e-05, 
                                0.0, 
                                -1.2890634405122961e-06, 
                                -2.219951899200523e-05, 
                                0.9999999997527599, 
                                0.0, 
                                1.974391166822964e-06, 
                                2.4114902035115064, 
                                1.5492555025110524, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": -1.0, 
                        "angularStiffness": -1.0, 
                        "linearDamping": -1.0, 
                        "linearStiffness": -1.0, 
                        "strength": -1.0
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 26
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                -1.0, 
                                1.2246467991473532e-16, 
                                0.0, 
                                0.0, 
                                -1.2246467991473532e-16, 
                                -1.0, 
                                0.0, 
                                -5.676221889435243e-17, 
                                2.411502167908824, 
                                -1.963410596116668e-16, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 17
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -0.9999999999471512, 
                                1.0199826322602606e-05, 
                                -1.2888370101808733e-06, 
                                0.0, 
                                1.0199797708519118e-05, 
                                0.9999999997015725, 
                                2.219953213705865e-05, 
                                0.0, 
                                1.28906344116849e-06, 
                                2.2199518990008645e-05, 
                                -0.9999999997527598, 
                                0.0, 
                                -2.262244316100956e-05, 
                                -1.196523909172131e-05, 
                                1.5492019560831594, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "JointComponent"
                }, 
                "LimitComponent": {
                    "members": {
                        "angularDamping": 10000.0, 
                        "angularStiffness": 1000000.0, 
                        "enabled": true, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "swing1": -0.01745329238474369, 
                        "swing2": -0.01745329238474369, 
                        "twist": 0.7853981852531433, 
                        "x": -1.0, 
                        "y": -1.0, 
                        "z": -1.0
                    }, 
                    "type": "LimitComponent"
                }, 
                "LimitUIComponent": {
                    "members": {
                        "angularDamping": 10000.0, 
                        "angularStiffness": 1000000.0, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "strength": 1.0
                    }, 
                    "type": "LimitUIComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|car_grp|polySurface48", 
                        "shortestPath": "polySurface48", 
                        "value": "rHingeConstraint1"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 27
        }, 
        "28": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 3, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }
                    }, 
                    "type": "ConstraintUIComponent"
                }, 
                "DriveComponent": {
                    "members": {
                        "acceleration": true, 
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "enabled": false, 
                        "linearDamping": 100.0, 
                        "linearStiffness": 1000.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                0.9999999999389055, 
                                1.0364623560458798e-05, 
                                3.842329599703976e-06, 
                                0.0, 
                                1.0733309649504556e-05, 
                                -0.9935569740762882, 
                                -0.11333375114750907, 
                                0.0, 
                                2.6429117031469923e-06, 
                                0.11333375118182593, 
                                -0.9935569741268342, 
                                0.0, 
                                9.895532658038553e-06, 
                                9.579689990157902e-06, 
                                -4.399989928955355, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": -1.0, 
                        "angularStiffness": -1.0, 
                        "linearDamping": -1.0, 
                        "linearStiffness": -1.0, 
                        "strength": -1.0
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 26
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                -1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 7
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                0.9999999999389055, 
                                1.0364623556040816e-05, 
                                3.842329600107407e-06, 
                                0.0, 
                                2.6429117040485695e-06, 
                                0.1133337511818222, 
                                -0.9935569741268347, 
                                0.0, 
                                -1.0733309645160751e-05, 
                                0.993556974076289, 
                                0.11333375114750543, 
                                0.0, 
                                9.895532457449006e-06, 
                                9.579690413374918e-06, 
                                -4.399990081787109, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "JointComponent"
                }, 
                "LimitComponent": {
                    "members": {
                        "angularDamping": 10000.0, 
                        "angularStiffness": 1000000.0, 
                        "enabled": true, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "swing1": -0.01745329238474369, 
                        "swing2": -0.01745329238474369, 
                        "twist": 0.7853981852531433, 
                        "x": -1.0, 
                        "y": -1.0, 
                        "z": -1.0
                    }, 
                    "type": "LimitComponent"
                }, 
                "LimitUIComponent": {
                    "members": {
                        "angularDamping": 10000.0, 
                        "angularStiffness": 1000000.0, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "strength": 1.0
                    }, 
                    "type": "LimitUIComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|car_grp|polySurface48", 
                        "shortestPath": "polySurface48", 
                        "value": "rHingeConstraint2"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 28
        }, 
        "29": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.21000000834465027, 
                                0.699999988079071, 
                                0.291666716337204, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ColorComponent"
                }, 
                "GeometryDescriptionComponent": {
                    "members": {
                        "extents": {
                            "type": "Vector3", 
                            "values": [
                                3.040010452270508, 
                                3.040010452270508, 
                                1.5999999046325684
                            ]
                        }, 
                        "length": 3.040010452270508, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "radius": 1.520005226135254, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "type": "ConvexHull"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|car_grp|polySurface509", 
                        "shortestPath": "polySurface509", 
                        "value": "rRigid3"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                4.310512065887451, 
                                1.9388923888163, 
                                -2.4040001034736633, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "RigidComponent": {
                    "members": {
                        "angularDamping": 1.0, 
                        "angularMass": {
                            "type": "Vector3", 
                            "values": [
                                -1.0, 
                                -1.0, 
                                -1.0
                            ]
                        }, 
                        "centerOfMass": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "collide": true, 
                        "disableGravity": false, 
                        "enableCCD": false, 
                        "enabled": true, 
                        "friction": 0.800000011920929, 
                        "kinematic": false, 
                        "linearDamping": 0.5, 
                        "mass": 1.0, 
                        "maxContactImpulse": 0.009999999776482582, 
                        "maxDepenetrationVelocity": -1.0, 
                        "parentRigid": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "positionIterations": 8, 
                        "restitution": 0.10000000149011612, 
                        "sleepThreshold": 4.999999873689376e-06, 
                        "thickness": 0.0, 
                        "velocityIterations": 1
                    }, 
                    "type": "RigidComponent"
                }, 
                "RigidUIComponent": {
                    "members": {
                        "airDensity": 1.0, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "shaded": false, 
                        "shapeIcon": "mesh"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 29
        }, 
        "30": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 3, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }
                    }, 
                    "type": "ConstraintUIComponent"
                }, 
                "DriveComponent": {
                    "members": {
                        "acceleration": true, 
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "enabled": false, 
                        "linearDamping": 100.0, 
                        "linearStiffness": 1000.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                1.4418291442996889e-06, 
                                -0.25882824563095297, 
                                -0.9659233609668649, 
                                0.0, 
                                -5.551115123125783e-17, 
                                -0.965923360967869, 
                                0.25882824563122203, 
                                0.0, 
                                -0.9999999999989606, 
                                -3.7318610790482154e-07, 
                                -1.3926964532728903e-06, 
                                0.0, 
                                2.3039999615776217, 
                                3.0501237150204474e-05, 
                                -4.3999891339692745, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": -1.0, 
                        "angularStiffness": -1.0, 
                        "linearDamping": -1.0, 
                        "linearStiffness": -1.0, 
                        "strength": -1.0
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 29
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                0.0, 
                                0.0, 
                                -1.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                -1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 7
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                0.9999999999989606, 
                                3.7318610791589364e-07, 
                                1.3926964531499754e-06, 
                                0.0, 
                                1.4418291444404692e-06, 
                                -0.2588282456309532, 
                                -0.9659233609668648, 
                                0.0, 
                                4.099607700975292e-17, 
                                0.9659233609678689, 
                                -0.2588282456312221, 
                                0.0, 
                                2.303999961577621, 
                                3.050123715020447e-05, 
                                -4.3999891339692745, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "JointComponent"
                }, 
                "LimitComponent": {
                    "members": {
                        "angularDamping": 10000.0, 
                        "angularStiffness": 1000000.0, 
                        "enabled": true, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "swing1": -0.01745329238474369, 
                        "swing2": -0.01745329238474369, 
                        "twist": 0.0, 
                        "x": -1.0, 
                        "y": -1.0, 
                        "z": -1.0
                    }, 
                    "type": "LimitComponent"
                }, 
                "LimitUIComponent": {
                    "members": {
                        "angularDamping": 10000.0, 
                        "angularStiffness": 1000000.0, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "strength": 1.0
                    }, 
                    "type": "LimitUIComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|car_grp|polySurface509", 
                        "shortestPath": "polySurface509", 
                        "value": "rHingeConstraint11"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 30
        }, 
        "31": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.21000000834465027, 
                                0.699999988079071, 
                                0.25899994373321533, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ColorComponent"
                }, 
                "GeometryDescriptionComponent": {
                    "members": {
                        "extents": {
                            "type": "Vector3", 
                            "values": [
                                3.040010452270508, 
                                3.040010452270508, 
                                1.6000001430511475
                            ]
                        }, 
                        "length": 3.040010452270508, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                -5.960464477539063e-08, 
                                1.1920928955078125e-07
                            ]
                        }, 
                        "radius": 1.520005226135254, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "type": "ConvexHull"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|car_grp|polySurface72", 
                        "shortestPath": "polySurface72", 
                        "value": "rRigid10"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                4.310513973236084, 
                                1.9389094953493506, 
                                2.303999960422516, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "RigidComponent": {
                    "members": {
                        "angularDamping": 1.0, 
                        "angularMass": {
                            "type": "Vector3", 
                            "values": [
                                -1.0, 
                                -1.0, 
                                -1.0
                            ]
                        }, 
                        "centerOfMass": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "collide": true, 
                        "disableGravity": false, 
                        "enableCCD": false, 
                        "enabled": true, 
                        "friction": 0.800000011920929, 
                        "kinematic": false, 
                        "linearDamping": 0.5, 
                        "mass": 1.0, 
                        "maxContactImpulse": -1.0, 
                        "maxDepenetrationVelocity": -1.0, 
                        "parentRigid": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "positionIterations": 8, 
                        "restitution": 0.10000000149011612, 
                        "sleepThreshold": 4.999999873689376e-06, 
                        "thickness": 0.0, 
                        "velocityIterations": 1
                    }, 
                    "type": "RigidComponent"
                }, 
                "RigidUIComponent": {
                    "members": {
                        "airDensity": 1.0, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "shaded": false, 
                        "shapeIcon": "mesh"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 31
        }, 
        "32": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 3, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }
                    }, 
                    "type": "ConstraintUIComponent"
                }, 
                "DriveComponent": {
                    "members": {
                        "acceleration": true, 
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "enabled": false, 
                        "linearDamping": 100.0, 
                        "linearStiffness": 1000.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                1.4418291442996889e-06, 
                                -0.25882824563095297, 
                                -0.9659233609668649, 
                                0.0, 
                                -5.551115123125783e-17, 
                                -0.965923360967869, 
                                0.25882824563122203, 
                                0.0, 
                                -0.9999999999989606, 
                                -3.7318610790482154e-07, 
                                -1.3926964532728903e-06, 
                                0.0, 
                                -2.4040001023109148, 
                                1.1727001332229037e-05, 
                                -4.3999931054829275, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": -1.0, 
                        "angularStiffness": -1.0, 
                        "linearDamping": -1.0, 
                        "linearStiffness": -1.0, 
                        "strength": -1.0
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 31
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                0.0, 
                                0.0, 
                                -1.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                -1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 7
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                0.9999999999989606, 
                                3.7318610791589364e-07, 
                                1.3926964531499754e-06, 
                                0.0, 
                                1.4418291444404692e-06, 
                                -0.2588282456309532, 
                                -0.9659233609668648, 
                                0.0, 
                                4.099607700975292e-17, 
                                0.9659233609678689, 
                                -0.2588282456312221, 
                                0.0, 
                                -2.4040001023109143, 
                                1.1727001332229035e-05, 
                                -4.3999931054829275, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "JointComponent"
                }, 
                "LimitComponent": {
                    "members": {
                        "angularDamping": 10000.0, 
                        "angularStiffness": 1000000.0, 
                        "enabled": true, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "swing1": -0.01745329238474369, 
                        "swing2": -0.01745329238474369, 
                        "twist": 0.0, 
                        "x": -1.0, 
                        "y": -1.0, 
                        "z": -1.0
                    }, 
                    "type": "LimitComponent"
                }, 
                "LimitUIComponent": {
                    "members": {
                        "angularDamping": 10000.0, 
                        "angularStiffness": 1000000.0, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "strength": 1.0
                    }, 
                    "type": "LimitUIComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|car_grp|polySurface72", 
                        "shortestPath": "polySurface72", 
                        "value": "rHingeConstraint10"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 32
        }, 
        "34": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 1, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }
                    }, 
                    "type": "ConstraintUIComponent"
                }, 
                "DriveComponent": {
                    "members": {
                        "acceleration": true, 
                        "angularDamping": 5.0, 
                        "angularStiffness": 1000.0, 
                        "enabled": true, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                12.60886220943522, 
                                7.464769095933753, 
                                2.303999900817864, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": 5.0, 
                        "angularStiffness": 1000.0, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "strength": 1.0
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 31
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "disableCollision": false, 
                        "parent": {
                            "type": "Entity", 
                            "value": 1048576
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "JointComponent"
                }, 
                "LimitComponent": {
                    "members": {
                        "angularDamping": 10000.0, 
                        "angularStiffness": 1000000.0, 
                        "enabled": false, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "swing1": -0.01745329238474369, 
                        "swing2": -0.01745329238474369, 
                        "twist": -0.01745329238474369, 
                        "x": -1.0, 
                        "y": -1.0, 
                        "z": -1.0
                    }, 
                    "type": "LimitComponent"
                }, 
                "LimitUIComponent": {
                    "members": {
                        "angularDamping": -1.0, 
                        "angularStiffness": -1.0, 
                        "linearDamping": -1.0, 
                        "linearStiffness": -1.0, 
                        "strength": -1.0
                    }, 
                    "type": "LimitUIComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|controls_grp|drive_ctrl", 
                        "shortestPath": "controls_grp|drive_ctrl", 
                        "value": "rAbsoluteConstraint1"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 34
        }, 
        "36": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 1, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }
                    }, 
                    "type": "ConstraintUIComponent"
                }, 
                "DriveComponent": {
                    "members": {
                        "acceleration": true, 
                        "angularDamping": 5.0, 
                        "angularStiffness": 1000.0, 
                        "enabled": true, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                12.608860302086587, 
                                7.464751929796058, 
                                -2.4040000438690257, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": 5.0, 
                        "angularStiffness": 1000.0, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "strength": 1.0
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 29
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "disableCollision": false, 
                        "parent": {
                            "type": "Entity", 
                            "value": 1048576
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "JointComponent"
                }, 
                "LimitComponent": {
                    "members": {
                        "angularDamping": 10000.0, 
                        "angularStiffness": 1000000.0, 
                        "enabled": false, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "swing1": -0.01745329238474369, 
                        "swing2": -0.01745329238474369, 
                        "twist": -0.01745329238474369, 
                        "x": -1.0, 
                        "y": -1.0, 
                        "z": -1.0
                    }, 
                    "type": "LimitComponent"
                }, 
                "LimitUIComponent": {
                    "members": {
                        "angularDamping": -1.0, 
                        "angularStiffness": -1.0, 
                        "linearDamping": -1.0, 
                        "linearStiffness": -1.0, 
                        "strength": -1.0
                    }, 
                    "type": "LimitUIComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|controls_grp|drive_ctrl1", 
                        "shortestPath": "controls_grp|drive_ctrl1", 
                        "value": "rAbsoluteConstraint1"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 36
        }, 
        "37": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.21000000834465027, 
                                0.6264999508857727, 
                                0.699999988079071, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ColorComponent"
                }, 
                "GeometryDescriptionComponent": {
                    "members": {
                        "extents": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "length": 1.0, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "radius": 0.5, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "type": "Box"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|obstacles_grp|pCube3", 
                        "shortestPath": "pCube3", 
                        "value": "rRigid20"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.9923518002095719, 
                                0.04890074806608862, 
                                0.11334293740413984, 
                                0.0, 
                                -0.05665818870710145, 
                                0.9961923646654596, 
                                0.06626177053679158, 
                                0.0, 
                                -0.10967111868332663, 
                                -0.07217679281331965, 
                                0.9913439142426461, 
                                0.0, 
                                -15.497817993164062, 
                                0.06837758421897888, 
                                -5.235118389129639, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "RigidComponent": {
                    "members": {
                        "angularDamping": 1.0, 
                        "angularMass": {
                            "type": "Vector3", 
                            "values": [
                                -1.0, 
                                -1.0, 
                                -1.0
                            ]
                        }, 
                        "centerOfMass": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "collide": true, 
                        "disableGravity": false, 
                        "enableCCD": false, 
                        "enabled": true, 
                        "friction": 0.800000011920929, 
                        "kinematic": false, 
                        "linearDamping": 0.5, 
                        "mass": 1.0, 
                        "maxContactImpulse": -1.0, 
                        "maxDepenetrationVelocity": -1.0, 
                        "parentRigid": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "positionIterations": 8, 
                        "restitution": 0.10000000149011612, 
                        "sleepThreshold": 4.999999873689376e-06, 
                        "thickness": 0.0, 
                        "velocityIterations": 1
                    }, 
                    "type": "RigidComponent"
                }, 
                "RigidUIComponent": {
                    "members": {
                        "airDensity": 1.0, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "shaded": true, 
                        "shapeIcon": "mesh"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                3.0000000000000004, 
                                3.0000000000000004, 
                                3.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                3.0000000000000004, 
                                3.0000000000000004, 
                                3.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 37
        }, 
        "38": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.5203333497047424, 
                                0.699999988079071, 
                                0.21000000834465027, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ColorComponent"
                }, 
                "GeometryDescriptionComponent": {
                    "members": {
                        "extents": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "length": 1.0, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "radius": 0.5, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "type": "Box"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|obstacles_grp|pCube4", 
                        "shortestPath": "pCube4", 
                        "value": "rRigid18"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.9886887095525781, 
                                0.04871949270621939, 
                                0.1418486751214352, 
                                0.0, 
                                -0.04921715919761209, 
                                0.9987881012709938, 
                                4.336808689942018e-19, 
                                0.0, 
                                -0.1416767688923443, 
                                -0.006981388825422033, 
                                0.9898883539906375, 
                                0.0, 
                                -22.03940773010254, 
                                -0.8513931035995483, 
                                4.069560527801514, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "RigidComponent": {
                    "members": {
                        "angularDamping": 1.0, 
                        "angularMass": {
                            "type": "Vector3", 
                            "values": [
                                -1.0, 
                                -1.0, 
                                -1.0
                            ]
                        }, 
                        "centerOfMass": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "collide": true, 
                        "disableGravity": false, 
                        "enableCCD": false, 
                        "enabled": true, 
                        "friction": 0.800000011920929, 
                        "kinematic": false, 
                        "linearDamping": 0.5, 
                        "mass": 1.0, 
                        "maxContactImpulse": -1.0, 
                        "maxDepenetrationVelocity": -1.0, 
                        "parentRigid": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "positionIterations": 8, 
                        "restitution": 0.10000000149011612, 
                        "sleepThreshold": 4.999999873689376e-06, 
                        "thickness": 0.0, 
                        "velocityIterations": 1
                    }, 
                    "type": "RigidComponent"
                }, 
                "RigidUIComponent": {
                    "members": {
                        "airDensity": 1.0, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "shaded": true, 
                        "shapeIcon": "mesh"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                2.0, 
                                2.0, 
                                2.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                2.0, 
                                2.0, 
                                2.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 38
        }, 
        "39": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.699999988079071, 
                                0.6836666464805603, 
                                0.21000000834465027, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ColorComponent"
                }, 
                "GeometryDescriptionComponent": {
                    "members": {
                        "extents": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "length": 1.0, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "radius": 0.5, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "type": "Box"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|obstacles_grp|pCube5", 
                        "shortestPath": "pCube5", 
                        "value": "rRigid19"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.8535295131319529, 
                                0.15105076138624213, 
                                -0.4986692668466426, 
                                0.0, 
                                -0.14298180315551084, 
                                0.9882176177568467, 
                                0.05460900952573223, 
                                0.0, 
                                0.5010424873991528, 
                                0.024690229638853124, 
                                0.8650704123834374, 
                                0.0, 
                                -18.787555694580078, 
                                -0.8641735315322876, 
                                1.9567919969558716, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "RigidComponent": {
                    "members": {
                        "angularDamping": 1.0, 
                        "angularMass": {
                            "type": "Vector3", 
                            "values": [
                                -1.0, 
                                -1.0, 
                                -1.0
                            ]
                        }, 
                        "centerOfMass": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "collide": true, 
                        "disableGravity": false, 
                        "enableCCD": false, 
                        "enabled": true, 
                        "friction": 0.800000011920929, 
                        "kinematic": false, 
                        "linearDamping": 0.5, 
                        "mass": 1.0, 
                        "maxContactImpulse": -1.0, 
                        "maxDepenetrationVelocity": -1.0, 
                        "parentRigid": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "positionIterations": 8, 
                        "restitution": 0.10000000149011612, 
                        "sleepThreshold": 4.999999873689376e-06, 
                        "thickness": 0.0, 
                        "velocityIterations": 1
                    }, 
                    "type": "RigidComponent"
                }, 
                "RigidUIComponent": {
                    "members": {
                        "airDensity": 1.0, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "shaded": true, 
                        "shapeIcon": "mesh"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.5, 
                                1.5, 
                                1.5
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.5, 
                                1.5, 
                                1.5
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 39
        }, 
        "40": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.6101667284965515, 
                                0.699999988079071, 
                                0.21000000834465027, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ColorComponent"
                }, 
                "GeometryDescriptionComponent": {
                    "members": {
                        "extents": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "length": 1.0, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "radius": 0.5, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "type": "Box"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|obstacles_grp|pCube6", 
                        "shortestPath": "pCube6", 
                        "value": "rRigid17"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.49090913513610135, 
                                0.1013968835275206, 
                                -0.8652900629562502, 
                                0.0, 
                                -0.38095280290990163, 
                                0.9182026477492357, 
                                -0.10853045481054066, 
                                0.0, 
                                0.7835069769919186, 
                                0.382913266520239, 
                                0.48938149467239334, 
                                0.0, 
                                -33.16505813598633, 
                                -1.38197922706604, 
                                3.2615814208984375, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "RigidComponent": {
                    "members": {
                        "angularDamping": 1.0, 
                        "angularMass": {
                            "type": "Vector3", 
                            "values": [
                                -1.0, 
                                -1.0, 
                                -1.0
                            ]
                        }, 
                        "centerOfMass": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "collide": true, 
                        "disableGravity": false, 
                        "enableCCD": false, 
                        "enabled": true, 
                        "friction": 0.800000011920929, 
                        "kinematic": false, 
                        "linearDamping": 0.5, 
                        "mass": 1.0, 
                        "maxContactImpulse": -1.0, 
                        "maxDepenetrationVelocity": -1.0, 
                        "parentRigid": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "positionIterations": 8, 
                        "restitution": 0.10000000149011612, 
                        "sleepThreshold": 4.999999873689376e-06, 
                        "thickness": 0.0, 
                        "velocityIterations": 1
                    }, 
                    "type": "RigidComponent"
                }, 
                "RigidUIComponent": {
                    "members": {
                        "airDensity": 1.0, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "shaded": true, 
                        "shapeIcon": "mesh"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.5, 
                                1.5000000000000002, 
                                1.5000000000000002
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.5, 
                                1.5000000000000002, 
                                1.5000000000000002
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 40
        }, 
        "41": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.6755000352859497, 
                                0.699999988079071, 
                                0.21000000834465027, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ColorComponent"
                }, 
                "GeometryDescriptionComponent": {
                    "members": {
                        "extents": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "length": 1.0, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "radius": 0.5, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "type": "Box"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|obstacles_grp|pCube7", 
                        "shortestPath": "pCube7", 
                        "value": "rRigid28"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.9987864657797302, 
                                0.04924952319405931, 
                                -0.00028326735364104437, 
                                0.0, 
                                -0.049249540551741834, 
                                0.9987865035989096, 
                                -5.462698626168397e-05, 
                                0.0, 
                                0.00028023325669993823, 
                                6.851148156463441e-05, 
                                0.9999999583877485, 
                                0.0, 
                                -20.84518814086914, 
                                -1.2931528091430664, 
                                0.2596154510974884, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "RigidComponent": {
                    "members": {
                        "angularDamping": 1.0, 
                        "angularMass": {
                            "type": "Vector3", 
                            "values": [
                                -1.0, 
                                -1.0, 
                                -1.0
                            ]
                        }, 
                        "centerOfMass": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "collide": true, 
                        "disableGravity": false, 
                        "enableCCD": false, 
                        "enabled": true, 
                        "friction": 0.800000011920929, 
                        "kinematic": false, 
                        "linearDamping": 0.5, 
                        "mass": 1.0, 
                        "maxContactImpulse": -1.0, 
                        "maxDepenetrationVelocity": -1.0, 
                        "parentRigid": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "positionIterations": 8, 
                        "restitution": 0.10000000149011612, 
                        "sleepThreshold": 4.999999873689376e-06, 
                        "thickness": 0.0, 
                        "velocityIterations": 1
                    }, 
                    "type": "RigidComponent"
                }, 
                "RigidUIComponent": {
                    "members": {
                        "airDensity": 1.0, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "shaded": true, 
                        "shapeIcon": "mesh"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 41
        }, 
        "42": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.21000000834465027, 
                                0.5121665596961975, 
                                0.699999988079071, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ColorComponent"
                }, 
                "GeometryDescriptionComponent": {
                    "members": {
                        "extents": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "length": 1.0, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "radius": 0.5, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "type": "Box"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|obstacles_grp|pCube8", 
                        "shortestPath": "pCube8", 
                        "value": "rRigid21"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.998779482444829, 
                                0.04939148235947639, 
                                0.00016406575852688553, 
                                0.0, 
                                -0.04939149242034368, 
                                0.9987794937474853, 
                                5.784468956953056e-05, 
                                0.0, 
                                -0.00016100848027831704, 
                                -6.587754177915613e-05, 
                                0.9999999848682093, 
                                0.0, 
                                -20.849864959716797, 
                                -0.2918776869773865, 
                                0.2600746750831604, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "RigidComponent": {
                    "members": {
                        "angularDamping": 1.0, 
                        "angularMass": {
                            "type": "Vector3", 
                            "values": [
                                -1.0, 
                                -1.0, 
                                -1.0
                            ]
                        }, 
                        "centerOfMass": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "collide": true, 
                        "disableGravity": false, 
                        "enableCCD": false, 
                        "enabled": true, 
                        "friction": 0.800000011920929, 
                        "kinematic": false, 
                        "linearDamping": 0.5, 
                        "mass": 1.0, 
                        "maxContactImpulse": -1.0, 
                        "maxDepenetrationVelocity": -1.0, 
                        "parentRigid": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "positionIterations": 8, 
                        "restitution": 0.10000000149011612, 
                        "sleepThreshold": 4.999999873689376e-06, 
                        "thickness": 0.0, 
                        "velocityIterations": 1
                    }, 
                    "type": "RigidComponent"
                }, 
                "RigidUIComponent": {
                    "members": {
                        "airDensity": 1.0, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "shaded": true, 
                        "shapeIcon": "mesh"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 42
        }, 
        "43": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.5121666789054871, 
                                0.699999988079071, 
                                0.21000000834465027, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ColorComponent"
                }, 
                "GeometryDescriptionComponent": {
                    "members": {
                        "extents": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "length": 1.0, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "radius": 0.5, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "type": "Box"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|obstacles_grp|pCube9", 
                        "shortestPath": "pCube9", 
                        "value": "rRigid22"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.9987868345366898, 
                                0.0492410904720869, 
                                -0.0004173311619885991, 
                                0.0, 
                                -0.04924110155261047, 
                                0.9987869210456359, 
                                -1.631147356648585e-05, 
                                0.0, 
                                0.00041602171159337004, 
                                3.684153117864883e-05, 
                                0.9999999127843148, 
                                0.0, 
                                -20.89887809753418, 
                                0.7069589495658875, 
                                0.2600248456001282, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "RigidComponent": {
                    "members": {
                        "angularDamping": 1.0, 
                        "angularMass": {
                            "type": "Vector3", 
                            "values": [
                                -1.0, 
                                -1.0, 
                                -1.0
                            ]
                        }, 
                        "centerOfMass": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "collide": true, 
                        "disableGravity": false, 
                        "enableCCD": false, 
                        "enabled": true, 
                        "friction": 0.800000011920929, 
                        "kinematic": false, 
                        "linearDamping": 0.5, 
                        "mass": 1.0, 
                        "maxContactImpulse": -1.0, 
                        "maxDepenetrationVelocity": -1.0, 
                        "parentRigid": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "positionIterations": 8, 
                        "restitution": 0.10000000149011612, 
                        "sleepThreshold": 4.999999873689376e-06, 
                        "thickness": 0.0, 
                        "velocityIterations": 1
                    }, 
                    "type": "RigidComponent"
                }, 
                "RigidUIComponent": {
                    "members": {
                        "airDensity": 1.0, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "shaded": true, 
                        "shapeIcon": "mesh"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 43
        }, 
        "44": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.39783331751823425, 
                                0.699999988079071, 
                                0.21000000834465027, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ColorComponent"
                }, 
                "GeometryDescriptionComponent": {
                    "members": {
                        "extents": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "length": 1.0, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "radius": 0.5, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "type": "Box"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|obstacles_grp|pCube10", 
                        "shortestPath": "pCube10", 
                        "value": "rRigid23"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.9987789166848067, 
                                0.04939821623434327, 
                                -0.000701297931829008, 
                                0.0, 
                                -0.04939819745354986, 
                                0.9987791628506724, 
                                4.408684775959104e-05, 
                                0.0, 
                                0.0007026195728998033, 
                                -9.390160335116852e-06, 
                                0.9999997531187499, 
                                0.0, 
                                -20.907962799072266, 
                                1.708006501197815, 
                                0.26021307706832886, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "RigidComponent": {
                    "members": {
                        "angularDamping": 1.0, 
                        "angularMass": {
                            "type": "Vector3", 
                            "values": [
                                -1.0, 
                                -1.0, 
                                -1.0
                            ]
                        }, 
                        "centerOfMass": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "collide": true, 
                        "disableGravity": false, 
                        "enableCCD": false, 
                        "enabled": true, 
                        "friction": 0.800000011920929, 
                        "kinematic": false, 
                        "linearDamping": 0.5, 
                        "mass": 1.0, 
                        "maxContactImpulse": -1.0, 
                        "maxDepenetrationVelocity": -1.0, 
                        "parentRigid": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "positionIterations": 8, 
                        "restitution": 0.10000000149011612, 
                        "sleepThreshold": 4.999999873689376e-06, 
                        "thickness": 0.0, 
                        "velocityIterations": 1
                    }, 
                    "type": "RigidComponent"
                }, 
                "RigidUIComponent": {
                    "members": {
                        "airDensity": 1.0, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "shaded": true, 
                        "shapeIcon": "mesh"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 44
        }, 
        "45": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.6918333172798157, 
                                0.699999988079071, 
                                0.21000000834465027, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ColorComponent"
                }, 
                "GeometryDescriptionComponent": {
                    "members": {
                        "extents": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "length": 1.0, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "radius": 0.5, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "type": "Box"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|obstacles_grp|pCube11", 
                        "shortestPath": "pCube11", 
                        "value": "rRigid24"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.9987821944564258, 
                                0.049336853230036615, 
                                -5.431541523830213e-05, 
                                0.0, 
                                -0.04933685803820796, 
                                0.9987821915447699, 
                                -9.106011342244857e-05, 
                                0.0, 
                                4.9756650015341766e-05, 
                                9.362897184242265e-05, 
                                0.9999999943789457, 
                                0.0, 
                                -20.90076446533203, 
                                2.7096221446990967, 
                                0.2585531175136566, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "RigidComponent": {
                    "members": {
                        "angularDamping": 1.0, 
                        "angularMass": {
                            "type": "Vector3", 
                            "values": [
                                -1.0, 
                                -1.0, 
                                -1.0
                            ]
                        }, 
                        "centerOfMass": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "collide": true, 
                        "disableGravity": false, 
                        "enableCCD": false, 
                        "enabled": true, 
                        "friction": 0.800000011920929, 
                        "kinematic": false, 
                        "linearDamping": 0.5, 
                        "mass": 1.0, 
                        "maxContactImpulse": -1.0, 
                        "maxDepenetrationVelocity": -1.0, 
                        "parentRigid": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "positionIterations": 8, 
                        "restitution": 0.10000000149011612, 
                        "sleepThreshold": 4.999999873689376e-06, 
                        "thickness": 0.0, 
                        "velocityIterations": 1
                    }, 
                    "type": "RigidComponent"
                }, 
                "RigidUIComponent": {
                    "members": {
                        "airDensity": 1.0, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "shaded": true, 
                        "shapeIcon": "mesh"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                0.9999999999999999, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                0.9999999999999999, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 45
        }, 
        "46": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.2998332977294922, 
                                0.699999988079071, 
                                0.21000000834465027, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ColorComponent"
                }, 
                "GeometryDescriptionComponent": {
                    "members": {
                        "extents": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "length": 1.0, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "radius": 0.5, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "type": "Box"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|obstacles_grp|pCube12", 
                        "shortestPath": "pCube12", 
                        "value": "rRigid25"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.9987763086932449, 
                                0.0494558322963689, 
                                -7.645240050891746e-05, 
                                0.0, 
                                -0.04945582034237631, 
                                0.998776300788609, 
                                0.00015105391291522213, 
                                0.0, 
                                8.382934275155128e-05, 
                                -0.00014708805337082398, 
                                0.9999999856688728, 
                                0.0, 
                                -20.950191497802734, 
                                3.708582639694214, 
                                0.25859951972961426, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "RigidComponent": {
                    "members": {
                        "angularDamping": 1.0, 
                        "angularMass": {
                            "type": "Vector3", 
                            "values": [
                                -1.0, 
                                -1.0, 
                                -1.0
                            ]
                        }, 
                        "centerOfMass": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "collide": true, 
                        "disableGravity": false, 
                        "enableCCD": false, 
                        "enabled": true, 
                        "friction": 0.800000011920929, 
                        "kinematic": false, 
                        "linearDamping": 0.5, 
                        "mass": 1.0, 
                        "maxContactImpulse": -1.0, 
                        "maxDepenetrationVelocity": -1.0, 
                        "parentRigid": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "positionIterations": 8, 
                        "restitution": 0.10000000149011612, 
                        "sleepThreshold": 4.999999873689376e-06, 
                        "thickness": 0.0, 
                        "velocityIterations": 1
                    }, 
                    "type": "RigidComponent"
                }, 
                "RigidUIComponent": {
                    "members": {
                        "airDensity": 1.0, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "shaded": true, 
                        "shapeIcon": "mesh"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 46
        }, 
        "47": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.21000000834465027, 
                                0.5774999856948853, 
                                0.699999988079071, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ColorComponent"
                }, 
                "GeometryDescriptionComponent": {
                    "members": {
                        "extents": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "length": 1.0, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "radius": 0.5, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "type": "Box"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|obstacles_grp|pCube13", 
                        "shortestPath": "pCube13", 
                        "value": "rRigid26"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.9987750625255309, 
                                0.049480639278223486, 
                                -0.000202024107658745, 
                                0.0, 
                                -0.04948062567678698, 
                                0.9987750810518541, 
                                7.178088831913318e-05, 
                                0.0, 
                                0.00020532840874328104, 
                                -6.169668197033113e-05, 
                                0.9999999770168817, 
                                0.0, 
                                -20.990583419799805, 
                                4.7078351974487305, 
                                0.259115993976593, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "RigidComponent": {
                    "members": {
                        "angularDamping": 1.0, 
                        "angularMass": {
                            "type": "Vector3", 
                            "values": [
                                -1.0, 
                                -1.0, 
                                -1.0
                            ]
                        }, 
                        "centerOfMass": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "collide": true, 
                        "disableGravity": false, 
                        "enableCCD": false, 
                        "enabled": true, 
                        "friction": 0.800000011920929, 
                        "kinematic": false, 
                        "linearDamping": 0.5, 
                        "mass": 1.0, 
                        "maxContactImpulse": -1.0, 
                        "maxDepenetrationVelocity": -1.0, 
                        "parentRigid": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "positionIterations": 8, 
                        "restitution": 0.10000000149011612, 
                        "sleepThreshold": 4.999999873689376e-06, 
                        "thickness": 0.0, 
                        "velocityIterations": 1
                    }, 
                    "type": "RigidComponent"
                }, 
                "RigidUIComponent": {
                    "members": {
                        "airDensity": 1.0, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "shaded": true, 
                        "shapeIcon": "mesh"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                0.9999999999999999, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                0.9999999999999999, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 47
        }, 
        "48": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.21000000834465027, 
                                0.699999988079071, 
                                0.6918333172798157, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ColorComponent"
                }, 
                "GeometryDescriptionComponent": {
                    "members": {
                        "extents": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "length": 1.0, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "radius": 0.5, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "type": "Box"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|obstacles_grp|pCube14", 
                        "shortestPath": "pCube14", 
                        "value": "rRigid27"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.9987747581425791, 
                                0.04948518304515285, 
                                0.0004462692240571631, 
                                0.0, 
                                -0.04948524898102132, 
                                0.9987748450518392, 
                                0.00013793100022740917, 
                                0.0, 
                                -0.0004388969343152432, 
                                -0.00015984574505753052, 
                                0.9999998909094034, 
                                0.0, 
                                -21.012184143066406, 
                                5.708052158355713, 
                                0.2602900564670563, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "RigidComponent": {
                    "members": {
                        "angularDamping": 1.0, 
                        "angularMass": {
                            "type": "Vector3", 
                            "values": [
                                -1.0, 
                                -1.0, 
                                -1.0
                            ]
                        }, 
                        "centerOfMass": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "collide": true, 
                        "disableGravity": false, 
                        "enableCCD": false, 
                        "enabled": true, 
                        "friction": 0.800000011920929, 
                        "kinematic": false, 
                        "linearDamping": 0.5, 
                        "mass": 1.0, 
                        "maxContactImpulse": -1.0, 
                        "maxDepenetrationVelocity": -1.0, 
                        "parentRigid": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "positionIterations": 8, 
                        "restitution": 0.10000000149011612, 
                        "sleepThreshold": 4.999999873689376e-06, 
                        "thickness": 0.0, 
                        "velocityIterations": 1
                    }, 
                    "type": "RigidComponent"
                }, 
                "RigidUIComponent": {
                    "members": {
                        "airDensity": 1.0, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "shaded": true, 
                        "shapeIcon": "mesh"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                0.9999999999999999
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                0.9999999999999999
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }
            }, 
            "id": 48
        }, 
        "1048576": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ColorComponent"
                }, 
                "GeometryDescriptionComponent": {
                    "members": {
                        "extents": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "length": 1.0, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "radius": 1.0, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.7071067811865476, 
                                0.7071067811865476
                            ]
                        }, 
                        "type": "Plane"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|rScene", 
                        "shortestPath": "rScene", 
                        "value": "rSceneShape"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "RestComponent"
                }, 
                "RigidComponent": {
                    "members": {
                        "angularDamping": 1.0, 
                        "angularMass": {
                            "type": "Vector3", 
                            "values": [
                                -1.0, 
                                -1.0, 
                                -1.0
                            ]
                        }, 
                        "centerOfMass": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "collide": false, 
                        "disableGravity": false, 
                        "enableCCD": false, 
                        "enabled": true, 
                        "friction": 0.5, 
                        "kinematic": true, 
                        "linearDamping": 0.5, 
                        "mass": 1.0, 
                        "maxContactImpulse": -1.0, 
                        "maxDepenetrationVelocity": -1.0, 
                        "parentRigid": {
                            "type": "Entity", 
                            "value": 0
                        }, 
                        "positionIterations": 8, 
                        "restitution": 0.5, 
                        "sleepThreshold": 4.999999873689376e-06, 
                        "thickness": 0.0, 
                        "velocityIterations": 1
                    }, 
                    "type": "RigidComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "ScaleComponent"
                }, 
                "SceneComponent": {
                    "members": {
                        "entity": {
                            "type": "Entity", 
                            "value": 1048576
                        }
                    }, 
                    "type": "SceneComponent"
                }, 
                "SolverComponent": {
                    "members": {
                        "airDensity": 1.0, 
                        "bounceThresholdVelocity": 1.0, 
                        "collisionDetectionType": "PCM", 
                        "enableCCD": false, 
                        "enableEnhancedFriction": false, 
                        "enableStabilisation": false, 
                        "enabled": true, 
                        "gravity": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                -98.19999694824219, 
                                0.0
                            ]
                        }, 
                        "groundFriction": 0.5, 
                        "groundRestitution": 0.5, 
                        "numThreads": 0, 
                        "positionIterations": 4, 
                        "spaceMultiplier": 1.0, 
                        "substeps": 4, 
                        "timeMultiplier": 1.0, 
                        "type": "TGS", 
                        "useGround": false, 
                        "velocityIterations": 1
                    }, 
                    "type": "SolverComponent"
                }
            }, 
            "id": 1048576
        }
    }, 
    "info": {
        "entitiesCount": 47, 
        "mayaVersion": "20200200", 
        "ragdollVersion": "2021.03.29", 
        "registryAlive": 49, 
        "registrySize": 49, 
        "serialisationTimeMs": 1.9122, 
        "timestamp": 1618053332
    }, 
    "schema": "ragdoll-1.0", 
    "ui": {
        "description": "", 
        "filename": "C:/Users/marcus/Documents/maya/projects/default/scenes/demo/ragcar2.rag", 
        "thumbnail": "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"
    }
}
```