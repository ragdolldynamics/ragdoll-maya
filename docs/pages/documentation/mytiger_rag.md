---
hidden: true
title: mytiger.rag
hide:
  - navigation # Hide navigation
  - toc        # Hide table of contents
---

<div class="vboxlayout align-center justify-center" markdown=1>

![image](https://user-images.githubusercontent.com/2152766/114277144-e87c7180-9a21-11eb-820d-7ef815c720ae.png)

A physicalised [Tiger Rig](https://www.cgspectrum.com/resources/tiger-animation-rig).

</div>

```json
{
    "entities": {
        "1": {
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
                        "angularDamping": 250.0, 
                        "angularStiffness": 2500.0, 
                        "enabled": true, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                -2.2648549702353193e-13, 
                                -0.9013341727488023, 
                                0.43312435747165284, 
                                0.0, 
                                6.661338147750939e-15, 
                                -0.433124357471653, 
                                -0.9013341727488025, 
                                0.0, 
                                1.0, 
                                -2.0133894551577214e-13, 
                                1.0413891970983968e-13, 
                                0.0, 
                                3.7381780064272526e-14, 
                                -7.683270290023827, 
                                -34.13870445259604, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "strength": 0.5
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 2
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -2.6645352591003757e-15, 
                                1.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                2.6645352591003757e-15, 
                                2.505887790353501e-13, 
                                0.0, 
                                2.505887790353501e-13, 
                                6.815758221109542e-28, 
                                -1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                -3.2311742677852644e-27, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 52
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                6.994405055138486e-15, 
                                -0.43312435747165073, 
                                -0.9013341727488036, 
                                0.0, 
                                2.414735078559716e-14, 
                                -0.9013341727488036, 
                                0.43312435747165073, 
                                0.0, 
                                -1.0000000000000002, 
                                -2.4868995751603513e-14, 
                                3.9968028886505635e-15, 
                                0.0, 
                                3.738178006427253e-14, 
                                -7.683270290023842, 
                                -34.138704452596045, 
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
                        "path": "|_:pup_Tiger_|_:grp_Tail_|_:grpCtrlFk_Tail_|_:ctrlFK_Tail_1_", 
                        "shortestPath": "_:ctrlFK_Tail_1_", 
                        "value": "rSocketConstraint15"
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
            "id": 1
        }, 
        "2": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.699999988079071, 
                                0.4059999883174896, 
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
                                21.567941665649414, 
                                7.190192699432373, 
                                7.190192699432373
                            ]
                        }, 
                        "length": 21.567941665649414, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                -2.842170943040401e-14, 
                                10.783970832824707, 
                                4.048065322618394e-15
                            ]
                        }, 
                        "radius": 3.5950963497161865, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.7071067811865466, 
                                0.7071067811865485, 
                                8.859651247257681e-14, 
                                8.859651247257657e-14
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Tail_|_:grpCtrlFk_Tail_|_:ctrlFK_Tail_1_", 
                        "shortestPath": "_:ctrlFK_Tail_1_", 
                        "value": "rRigid19"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                -5.9604643443122995e-08, 
                                -0.894608708769746, 
                                0.44685037562177854, 
                                0.0, 
                                8.881784197001254e-16, 
                                -0.4468503756217794, 
                                -0.8946087087697475, 
                                0.0, 
                                0.9999999999999983, 
                                -5.3322832593849525e-08, 
                                2.6634358052390894e-08, 
                                0.0, 
                                -3.162283419072312e-14, 
                                90.80577681331164, 
                                -90.06314527021878, 
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
                            "value": 52
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
                        "shapeIcon": "joint"
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
            "id": 2
        }, 
        "3": {
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
                        "angularDamping": 250.0, 
                        "angularStiffness": 2500.0, 
                        "enabled": true, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                0.9994013431104898, 
                                0.03459704306655591, 
                                0.0, 
                                0.0, 
                                -0.03459704306655591, 
                                0.9994013431104898, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                -7.105427357601002e-14, 
                                21.56794166564942, 
                                9.09398606728864e-16, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "strength": 0.5
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 4
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -1.9984014443252818e-15, 
                                1.0, 
                                0.0, 
                                0.0, 
                                -1.0, 
                                -1.9984014443252818e-15, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                -1.4210854715202007e-14, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 2
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -0.03459704306655831, 
                                0.9994013431104897, 
                                0.0, 
                                0.0, 
                                -0.9994013431104897, 
                                -0.03459704306655831, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                -5.684341886080802e-14, 
                                21.567942357508315, 
                                9.09398652934656e-16, 
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
                        "path": "|_:pup_Tiger_|_:grp_Tail_|_:grpCtrlFk_Tail_|_:ctrlFK_Tail_1_|_:ctrlFK_Tail_2_", 
                        "shortestPath": "_:ctrlFK_Tail_2_", 
                        "value": "rSocketConstraint16"
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
            "id": 3
        }, 
        "4": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.21000000834465027, 
                                0.5448333621025085, 
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
                                21.57111358642578, 
                                7.190192699432373, 
                                7.190192699432373
                            ]
                        }, 
                        "length": 21.57111358642578, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                -2.842170943040401e-14, 
                                10.78555679321289, 
                                -1.3228475389745475e-13
                            ]
                        }, 
                        "radius": 3.5950963497161865, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.7071067811865483, 
                                0.7071067811865467
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Tail_|_:grpCtrlFk_Tail_|_:ctrlFK_Tail_1_|_:ctrlFK_Tail_2_", 
                        "shortestPath": "_:ctrlFK_Tail_2_", 
                        "value": "rRigid20"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                -5.9573649346944535e-08, 
                                -0.9085521068845067, 
                                0.4177715513001341, 
                                0.0, 
                                1.9219393854186255e-09, 
                                -0.417771551300135, 
                                -0.9085521068845083, 
                                0.0, 
                                0.9999999999999983, 
                                -5.332283292691643e-08, 
                                2.663435783034629e-08, 
                                0.0, 
                                -1.1557251190381608e-14, 
                                81.16813366947021, 
                                -109.35801433348968, 
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
                            "value": 2
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
                        "shapeIcon": "joint"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0000000000000002, 
                                1.0000000000000002, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0000000000000002, 
                                1.0000000000000002, 
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
            "id": 4
        }, 
        "5": {
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
                        "angularDamping": 250.0, 
                        "angularStiffness": 2500.0, 
                        "enabled": true, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                0.9998600431815514, 
                                -0.016730034339059393, 
                                -0.0, 
                                0.0, 
                                0.016730034339059393, 
                                0.9998600431815514, 
                                0.0, 
                                0.0, 
                                0.0, 
                                -0.0, 
                                1.0, 
                                0.0, 
                                -5.684341886080802e-14, 
                                21.57111358642581, 
                                -2.6335354795341917e-13, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "strength": 0.5
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 6
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                2.220446049250313e-16, 
                                1.0000000000000002, 
                                7.888609052210118e-31, 
                                0.0, 
                                1.0000000000000002, 
                                -4.440892098500626e-16, 
                                -1.3001051765566551e-14, 
                                0.0, 
                                -1.3001051765566551e-14, 
                                3.944304526105059e-30, 
                                -1.0, 
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
                            "value": 4
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                0.016730034339059507, 
                                0.9998600431815515, 
                                0.0, 
                                0.0, 
                                0.9998600431815515, 
                                -0.01673003433905973, 
                                -1.3001051765566553e-14, 
                                0.0, 
                                -1.2999232179724958e-14, 
                                2.1750804248182136e-16, 
                                -1.0, 
                                0.0, 
                                -5.684341886080803e-14, 
                                21.571113228546626, 
                                -2.6335355315213946e-13, 
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
                        "path": "|_:pup_Tiger_|_:grp_Tail_|_:grpCtrlFk_Tail_|_:ctrlFK_Tail_1_|_:ctrlFK_Tail_2_|_:ctrlFK_Tail_3_", 
                        "shortestPath": "_:ctrlFK_Tail_3_", 
                        "value": "rSocketConstraint17"
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
            "id": 5
        }, 
        "6": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.21000000834465027, 
                                0.699999988079071, 
                                0.34066668152809143, 
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
                                21.571224212646484, 
                                7.190192699432373, 
                                7.190192699432373
                            ]
                        }, 
                        "length": 21.571224212646484, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                10.785612106323242, 
                                -1.3179030349669274e-13
                            ]
                        }, 
                        "radius": 3.5950963497161865, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                -0.7071067811865476, 
                                -0.7071067811865476, 
                                4.596565932994722e-15, 
                                4.596565932994722e-15
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Tail_|_:grpCtrlFk_Tail_|_:ctrlFK_Tail_1_|_:ctrlFK_Tail_2_|_:ctrlFK_Tail_3_", 
                        "shortestPath": "_:ctrlFK_Tail_3_", 
                        "value": "rRigid21"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                -5.9588986855985127e-08, 
                                -0.9046150454153568, 
                                0.426229538638711, 
                                0.0, 
                                1.3660746422949899e-09, 
                                -0.4262295386387118, 
                                -0.9046150454153583, 
                                0.0, 
                                0.9999999999999982, 
                                -5.3322832704871814e-08, 
                                2.6634358052390894e-08, 
                                0.0, 
                                4.145810249872009e-08, 
                                72.15633623270946, 
                                -128.95649470513004, 
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
                            "value": 4
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
                        "shapeIcon": "joint"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0000000000000002, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0000000000000002, 
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
            "id": 6
        }, 
        "7": {
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
                        "angularDamping": 250.0, 
                        "angularStiffness": 2500.0, 
                        "enabled": true, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                0.9999481012611428, 
                                -0.010187972528203696, 
                                -0.0, 
                                0.0, 
                                0.010187972528203696, 
                                0.9999481012611428, 
                                0.0, 
                                0.0, 
                                0.0, 
                                -0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                21.5712242126465, 
                                -2.6791275361398904e-13, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "strength": 0.5
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 8
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -1.1102230246251565e-15, 
                                1.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                1.1102230246251565e-15, 
                                4.180104111488237e-13, 
                                0.0, 
                                4.180104111488237e-13, 
                                4.543838814073028e-28, 
                                -1.0, 
                                0.0, 
                                0.0, 
                                2.8421709430404014e-14, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 6
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                0.010187972528202693, 
                                0.9999481012611428, 
                                0.0, 
                                0.0, 
                                0.9999481012611428, 
                                -0.010187972528202582, 
                                4.180104111488237e-13, 
                                0.0, 
                                4.1798871693565585e-13, 
                                -4.258678585286902e-15, 
                                -1.0, 
                                0.0, 
                                0.0, 
                                21.571224472131608, 
                                -2.6791276333527086e-13, 
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
                        "path": "|_:pup_Tiger_|_:grp_Tail_|_:grpCtrlFk_Tail_|_:ctrlFK_Tail_1_|_:ctrlFK_Tail_2_|_:ctrlFK_Tail_3_|_:ctrlFK_Tail_4_", 
                        "shortestPath": "_:ctrlFK_Tail_4_", 
                        "value": "rSocketConstraint18"
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
            "id": 7
        }, 
        "8": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.21000000834465027, 
                                0.6428333520889282, 
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
                                21.5712947845459, 
                                7.190192699432373, 
                                7.190192699432373
                            ]
                        }, 
                        "length": 21.5712947845459, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                -2.842170943040401e-14, 
                                10.78564739227295, 
                                -8.37023321747371e-14
                            ]
                        }, 
                        "radius": 3.5950963497161865, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.7071067811865471, 
                                0.707106781186548, 
                                1.4747497967321836e-13, 
                                1.4747497967321818e-13
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Tail_|_:grpCtrlFk_Tail_|_:ctrlFK_Tail_1_|_:ctrlFK_Tail_2_|_:ctrlFK_Tail_3_|_:ctrlFK_Tail_4_", 
                        "shortestPath": "_:ctrlFK_Tail_4_", 
                        "value": "rRigid22"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                -1.1920927667219416e-07, 
                                -0.9029151996015902, 
                                0.4298187319422067, 
                                0.0, 
                                1.1294144508511297e-09, 
                                -0.42981873194220976, 
                                -0.9029151996015965, 
                                0.0, 
                                0.9999999999999929, 
                                -1.0715042425557544e-07, 
                                5.225814558862396e-08, 
                                0.0, 
                                7.0925738208372e-08, 
                                62.962043178080705, 
                                -148.47014891065228, 
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
                            "value": 6
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
                        "shapeIcon": "joint"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0000000000000002, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0000000000000002, 
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
                        "angularDamping": 250.0, 
                        "angularStiffness": 2500.0, 
                        "enabled": true, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                0.9999842649549091, 
                                -0.0056097988012212, 
                                -0.0, 
                                0.0, 
                                0.0056097988012212, 
                                0.9999842649549091, 
                                0.0, 
                                0.0, 
                                0.0, 
                                -0.0, 
                                1.0, 
                                0.0, 
                                -4.263256414560601e-14, 
                                21.5712947845459, 
                                -1.7620875190828649e-13, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "strength": 0.5
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 10
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                7.771561172376096e-16, 
                                1.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                -6.661338147750939e-16, 
                                4.859560602558833e-13, 
                                0.0, 
                                4.859560602558833e-13, 
                                -4.0389678347315804e-28, 
                                -1.0, 
                                0.0, 
                                0.0, 
                                2.8421709430404014e-14, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 8
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                0.005609798801221366, 
                                0.9999842649549092, 
                                0.0, 
                                0.0, 
                                0.9999842649549092, 
                                -0.005609798801221588, 
                                4.859560602558834e-13, 
                                0.0, 
                                4.85948413715363e-13, 
                                -2.726115724269761e-15, 
                                -1.0, 
                                0.0, 
                                -1.4210854715202004e-14, 
                                21.57129482036493, 
                                -1.762087508006464e-13, 
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
                        "path": "|_:pup_Tiger_|_:grp_Tail_|_:grpCtrlFk_Tail_|_:ctrlFK_Tail_1_|_:ctrlFK_Tail_2_|_:ctrlFK_Tail_3_|_:ctrlFK_Tail_4_|_:ctrlFK_Tail_5_", 
                        "shortestPath": "_:ctrlFK_Tail_5_", 
                        "value": "rSocketConstraint19"
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
            "id": 9
        }, 
        "10": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.21000000834465027, 
                                0.699999988079071, 
                                0.5856666564941406, 
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
                                21.571313858032227, 
                                7.190192699432373, 
                                7.190192699432373
                            ]
                        }, 
                        "length": 21.571313858032227, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                1.4210854715202004e-14, 
                                10.785656929016113, 
                                -5.805236526950155e-14
                            ]
                        }, 
                        "radius": 3.5950963497161865, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.7071067811865477, 
                                0.7071067811865475, 
                                1.716544035369484e-13, 
                                1.7165440353694844e-13
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Tail_|_:grpCtrlFk_Tail_|_:ctrlFK_Tail_1_|_:ctrlFK_Tail_2_|_:ctrlFK_Tail_3_|_:ctrlFK_Tail_4_|_:ctrlFK_Tail_5_", 
                        "shortestPath": "_:ctrlFK_Tail_5_", 
                        "value": "rRigid23"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                5.9604644331301415e-08, 
                                -0.9014731579705597, 
                                0.4328350095112253, 
                                0.0, 
                                7.308604277334041e-10, 
                                -0.4328350095112259, 
                                -0.9014731579705615, 
                                0.0, 
                                0.9999999999999982, 
                                5.404832886801714e-08, 
                                -2.5140125536893265e-08, 
                                0.0, 
                                9.52884935638712e-08, 
                                53.690296592039914, 
                                -167.947198879047, 
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
                            "value": 8
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
                        "shapeIcon": "joint"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0000000000000002, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0000000000000002, 
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
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 51
                        }
                    }, 
                    "type": "ConstraintUIComponent"
                }, 
                "DriveComponent": {
                    "members": {
                        "acceleration": true, 
                        "angularDamping": 250.0, 
                        "angularStiffness": 2500.0, 
                        "enabled": true, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                0.9657425801293669, 
                                -0.18847673933300135, 
                                0.17837541213820185, 
                                0.0, 
                                0.1835739001807799, 
                                0.9820315895179306, 
                                0.043755918014639766, 
                                0.0, 
                                -0.18341726226691574, 
                                -0.00951188305682351, 
                                0.9829891311623048, 
                                0.0, 
                                -12.514599999999927, 
                                -5.1653471033350655, 
                                -11.728359182377176, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "strength": 0.5
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
                                3.0147308671679696e-07, 
                                -0.9999999999999518, 
                                -7.361100118341568e-08, 
                                0.0, 
                                0.8209441897359857, 
                                2.0546007606370154e-07, 
                                0.5710084389382383, 
                                0.0, 
                                -0.5710084389381956, 
                                -2.3257420034283882e-07, 
                                0.8209441897360081, 
                                0.0, 
                                0.0, 
                                1.4210854715202004e-14, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 52
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -0.1835735955338471, 
                                -0.9820316456383683, 
                                -0.04375593659806587, 
                                0.0, 
                                0.6880879930535927, 
                                -0.16016004778316706, 
                                0.7077313564549568, 
                                0.0, 
                                -0.7020225415456791, 
                                0.09981285517853972, 
                                0.7051253399948503, 
                                0.0, 
                                -12.514599999999927, 
                                -5.165347103335051, 
                                -11.728359182377176, 
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
                        "path": "|_:pup_Tiger_|_:grp_Rt_HindLeg_|_:grpCtrlFk_Rt_HindLeg_|_:ctrlFK_Rt_HindLeg_1_", 
                        "shortestPath": "_:ctrlFK_Rt_HindLeg_1_", 
                        "value": "rSocketConstraint11"
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
                                0.699999988079071, 
                                0.3488333225250244, 
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
                                42.714202880859375, 
                                8.542840957641602, 
                                8.542840957641602
                            ]
                        }, 
                        "length": 42.714202880859375, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                6.4385912992293015e-06, 
                                -21.357101440429688, 
                                -1.5721176396255032e-06
                            ]
                        }, 
                        "radius": 4.271420478820801, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.2115749904153387, 
                                -0.21157487696497734, 
                                -0.674711731557049, 
                                0.674711919390263
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Rt_HindLeg_|_:grpCtrlFk_Rt_HindLeg_|_:ctrlFK_Rt_HindLeg_1_", 
                        "shortestPath": "_:ctrlFK_Rt_HindLeg_1_", 
                        "value": "rRigid15"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.9656697884613963, 
                                -0.18691671616493827, 
                                0.18039955895466614, 
                                0.0, 
                                0.18201082132402047, 
                                0.9823327118923837, 
                                0.04352590110624457, 
                                0.0, 
                                -0.18534810647502625, 
                                -0.009196975822029009, 
                                0.9826298871201972, 
                                0.0, 
                                -12.514599999999996, 
                                93.32370000000043, 
                                -67.65279999999991, 
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
                            "value": 52
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
                        "shapeIcon": "joint"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                0.9999999999999999, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                0.9999999999999999, 
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
                            "value": 51
                        }
                    }, 
                    "type": "ConstraintUIComponent"
                }, 
                "DriveComponent": {
                    "members": {
                        "acceleration": true, 
                        "angularDamping": 160.00001525878906, 
                        "angularStiffness": 1600.0001220703125, 
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
                                0.7693171234831935, 
                                0.6388670937805021, 
                                0.0, 
                                0.0, 
                                -0.6388670937805021, 
                                0.7693171234831935, 
                                0.0, 
                                1.2877182612669458e-05, 
                                -42.714202880859354, 
                                -3.1442352650401517e-06, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "strength": 0.4000000059604645
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 14
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -0.9995924922360893, 
                                -0.024033337907173553, 
                                -0.015402861236910448, 
                                0.0, 
                                0.02264844434498108, 
                                -0.9961639161454063, 
                                0.08452514500786329, 
                                0.0, 
                                -0.01737519594123181, 
                                0.08414184950954925, 
                                0.996302289331464, 
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
                                -0.9995453151162219, 
                                -0.009674232232181952, 
                                -0.028558225784009534, 
                                0.0, 
                                0.02406293831564036, 
                                -0.8266713473716145, 
                                -0.5621703108795562, 
                                0.0, 
                                -0.018169700845923197, 
                                -0.5626018953625351, 
                                0.8265282628595665, 
                                0.0, 
                                1.2877182598458601e-05, 
                                -42.714202880859375, 
                                -3.1442352792510064e-06, 
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
                        "path": "|_:pup_Tiger_|_:grp_Rt_HindLeg_|_:grpCtrlFk_Rt_HindLeg_|_:ctrlFK_Rt_HindLeg_1_|_:ctrlFK_Rt_HindLeg_2_", 
                        "shortestPath": "_:ctrlFK_Rt_HindLeg_2_", 
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
            "id": 13
        }, 
        "14": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.699999988079071, 
                                0.2998333275318146, 
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
                                32.432926177978516, 
                                7.491068363189697, 
                                7.491068363189697
                            ]
                        }, 
                        "length": 32.432926177978516, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                1.514915766165359e-05, 
                                -16.216463088989258, 
                                1.0198138625128195e-05
                            ]
                        }, 
                        "radius": 3.7455341815948486, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                -0.5000002275026434, 
                                0.49999944597291096, 
                                -0.5000000869348195, 
                                0.5000002395892027
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Rt_HindLeg_|_:grpCtrlFk_Rt_HindLeg_|_:ctrlFK_Rt_HindLeg_1_|_:ctrlFK_Rt_HindLeg_2_", 
                        "shortestPath": "_:ctrlFK_Rt_HindLeg_2_", 
                        "value": "rRigid16"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.9655307212325601, 
                                -0.1862198167822468, 
                                0.18185875341516738, 
                                0.0, 
                                0.023070964824964176, 
                                0.7571572559193276, 
                                0.6528251070468715, 
                                0.0, 
                                -0.25926464652585685, 
                                -0.6261270395425359, 
                                0.735354862236949, 
                                0.0, 
                                -20.289034325784243, 
                                51.36413781658179, 
                                -69.51197498366723, 
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
                            "value": 12
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
                        "shapeIcon": "joint"
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
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 51
                        }
                    }, 
                    "type": "ConstraintUIComponent"
                }, 
                "DriveComponent": {
                    "members": {
                        "acceleration": true, 
                        "angularDamping": 90.0, 
                        "angularStiffness": 900.0000610351562, 
                        "enabled": true, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                -0.0, 
                                0.0, 
                                -0.0, 
                                0.5739372799164537, 
                                -0.8188992604234675, 
                                0.0, 
                                0.0, 
                                0.8188992604234675, 
                                0.5739372799164537, 
                                0.0, 
                                3.029831531620175e-05, 
                                -32.432926177978516, 
                                2.039627725025639e-05, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "strength": 0.30000001192092896
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 16
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -0.9995924922360893, 
                                -0.024033337907173553, 
                                -0.015402861236910448, 
                                0.0, 
                                0.02264844434498108, 
                                -0.9961639161454063, 
                                0.08452514500786329, 
                                0.0, 
                                -0.01737519594123181, 
                                0.08414184950954925, 
                                0.996302289331464, 
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
                                -0.999640636621342, 
                                -0.024730778990274163, 
                                0.01034341267729244, 
                                0.0, 
                                0.024995328160323543, 
                                -0.7204849650266933, 
                                0.6930199482992121, 
                                0.0, 
                                -0.00968664985618334, 
                                0.6930294393032803, 
                                0.720844203051911, 
                                0.0, 
                                3.029831532330718e-05, 
                                -32.432926177978516, 
                                2.039627725025639e-05, 
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
                        "twist": 1.0413981676101685, 
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
                        "path": "|_:pup_Tiger_|_:grp_Rt_HindLeg_|_:grpCtrlFk_Rt_HindLeg_|_:ctrlFK_Rt_HindLeg_1_|_:ctrlFK_Rt_HindLeg_2_|_:ctrlFK_Rt_HindLeg_3_", 
                        "shortestPath": "_:ctrlFK_Rt_HindLeg_3_", 
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
            "id": 15
        }, 
        "16": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.21000000834465027, 
                                0.22633332014083862, 
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
                                19.880685806274414, 
                                7.491068363189697, 
                                7.491068363189697
                            ]
                        }, 
                        "length": 19.880685806274414, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                -1.4533057765220292e-05, 
                                -9.940342903137207, 
                                8.044727337619406e-07
                            ]
                        }, 
                        "radius": 3.7455341815948486, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.5000001556259337, 
                                -0.5000009271056506, 
                                -0.49999980390737875, 
                                0.49999911335932884
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Rt_HindLeg_|_:grpCtrlFk_Rt_HindLeg_|_:ctrlFK_Rt_HindLeg_1_|_:ctrlFK_Rt_HindLeg_2_|_:ctrlFK_Rt_HindLeg_3_", 
                        "shortestPath": "_:ctrlFK_Rt_HindLeg_3_", 
                        "value": "rRigid17"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.9654693320085435, 
                                -0.1876614038689286, 
                                0.1806991047263925, 
                                0.0, 
                                0.22450784881575098, 
                                0.9512019013314558, 
                                -0.21168648687043606, 
                                0.0, 
                                -0.13215594867844888, 
                                0.2449451783590897, 
                                0.9604877223720941, 
                                0.0, 
                                -21.03726921952759, 
                                26.80729530909051, 
                                -90.68498186545077, 
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
                            "value": 14
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
                        "shapeIcon": "joint"
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
            "id": 16
        }, 
        "17": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 51
                        }
                    }, 
                    "type": "ConstraintUIComponent"
                }, 
                "DriveComponent": {
                    "members": {
                        "acceleration": true, 
                        "angularDamping": 40.000003814697266, 
                        "angularStiffness": 400.0000305175781, 
                        "enabled": true, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                0.9805034775093397, 
                                0.16763105054102037, 
                                0.10253175842930622, 
                                0.0, 
                                -0.06958300161932186, 
                                0.7841684792037189, 
                                -0.6166344152810254, 
                                0.0, 
                                -0.18376924791089827, 
                                0.5974777210221655, 
                                0.7805441924737012, 
                                0.0, 
                                -2.9066115530440584e-05, 
                                -19.880685806274414, 
                                1.608945581210719e-06, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "strength": 0.20000000298023224
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 18
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                6.845605295513479e-06, 
                                -0.9999999999750488, 
                                -1.7435984360214545e-06, 
                                0.0, 
                                0.27014476769356066, 
                                1.7053350220841423e-07, 
                                0.9628197154648233, 
                                0.0, 
                                -0.9628197154405025, 
                                -7.06210773732119e-06, 
                                0.27014476768798756, 
                                0.0, 
                                0.0, 
                                0.0, 
                                -7.105427357601002e-15, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 16
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                0.0695900341771567, 
                                -0.7841683734093657, 
                                0.6166337562019546, 
                                0.0, 
                                0.0879412173035009, 
                                0.6205481142847606, 
                                0.77922165021052, 
                                0.0, 
                                -0.9936918885863971, 
                                1.461881099507067e-06, 
                                0.11214468581017245, 
                                0.0, 
                                -2.906611583597396e-05, 
                                -19.880685406885554, 
                                1.6089455527890095e-06, 
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
                        "path": "|_:pup_Tiger_|_:grp_Rt_HindLeg_|_:grpCtrlFk_Rt_HindLeg_|_:ctrlFK_Rt_HindLeg_1_|_:ctrlFK_Rt_HindLeg_2_|_:ctrlFK_Rt_HindLeg_3_|_:ctrlFK_Rt_HindLeg_4_", 
                        "shortestPath": "_:ctrlFK_Rt_HindLeg_4_", 
                        "value": "rSocketConstraint14"
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
            "id": 17
        }, 
        "18": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.21000000834465027, 
                                0.699999988079071, 
                                0.5774999856948853, 
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
                                9.57519245147705, 
                                7.491068363189697, 
                                7.491068363189697
                            ]
                        }, 
                        "length": 9.57519245147705, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                3.277399082435295e-05, 
                                -4.787596225738525, 
                                -8.347645234607626e-06
                            ]
                        }, 
                        "radius": 3.7455341815948486, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.42715977905925523, 
                                -0.42715587238156383, 
                                -0.5635019413340978, 
                                0.5635050540649091
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Rt_HindLeg_|_:grpCtrlFk_Rt_HindLeg_|_:ctrlFK_Rt_HindLeg_1_|_:ctrlFK_Rt_HindLeg_2_|_:ctrlFK_Rt_HindLeg_3_|_:ctrlFK_Rt_HindLeg_4_", 
                        "shortestPath": "_:ctrlFK_Rt_HindLeg_4_", 
                        "value": "rRigid18"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.9704627726165137, 
                                -0.0005669444993102041, 
                                0.24125025500381025, 
                                0.0, 
                                0.19048586689821856, 
                                0.615452177780438, 
                                -0.7648096177332959, 
                                0.0, 
                                -0.1480443902263876, 
                                0.7881740261130474, 
                                0.5973814217761098, 
                                0.0, 
                                -25.500667408285324, 
                                7.896755398980002, 
                                -86.47651312193949, 
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
                            "value": 16
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
                        "shapeIcon": "joint"
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
            "id": 18
        }, 
        "19": {
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
                        "angularDamping": 250.0, 
                        "angularStiffness": 2500.0, 
                        "enabled": true, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                0.965742580129367, 
                                0.18847673933300085, 
                                -0.17837541213820174, 
                                0.0, 
                                0.18357390018077907, 
                                -0.9820315895179306, 
                                -0.04375591801464156, 
                                0.0, 
                                -0.18341726226691596, 
                                0.009511883056825408, 
                                -0.9829891311623047, 
                                0.0, 
                                12.51456106373762, 
                                -5.165311352010676, 
                                -11.728319906354464, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "strength": 0.5
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 20
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                -0.8209442641259262, 
                                0.0, 
                                -0.5710083319871451, 
                                0.0, 
                                -0.5710083319871451, 
                                0.0, 
                                0.8209442641259261, 
                                0.0, 
                                0.0, 
                                -1.4210854715202004e-14, 
                                1.4210854715202004e-14, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 52
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                0.18357390018077957, 
                                -0.9820315895179306, 
                                -0.04375591801464007, 
                                0.0, 
                                -0.6880880467946962, 
                                -0.16016026255491833, 
                                0.7077312556024353, 
                                0.0, 
                                -0.7020224092083366, 
                                -0.09981306270837659, 
                                -0.7051254423732676, 
                                0.0, 
                                12.51456106373762, 
                                -5.165311352010676, 
                                -11.728319906354457, 
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
                        "path": "|_:pup_Tiger_|_:grp_Lf_HindLeg_|_:grpCtrlFk_Lf_HindLeg_|_:ctrlFK_Lf_HindLeg_1_", 
                        "shortestPath": "_:ctrlFK_Lf_HindLeg_1_", 
                        "value": "rSocketConstraint"
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
            "id": 19
        }, 
        "20": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.699999988079071, 
                                0.4141666293144226, 
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
                                42.71420669555664, 
                                8.542841911315918, 
                                8.542841911315918
                            ]
                        }, 
                        "length": 42.71420669555664, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                21.35710334777832, 
                                -1.4210854715202004e-14
                            ]
                        }, 
                        "radius": 4.271420955657959, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                -0.21157488974005983, 
                                -0.21157488974005983, 
                                0.674711839255457, 
                                0.674711839255457
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Lf_HindLeg_|_:grpCtrlFk_Lf_HindLeg_|_:ctrlFK_Lf_HindLeg_1_", 
                        "shortestPath": "_:ctrlFK_Lf_HindLeg_1_", 
                        "value": "rRigid"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.9656616967844748, 
                                0.1868759825717776, 
                                -0.1804850534009996, 
                                0.0, 
                                0.1819693542866576, 
                                -0.982340578108069, 
                                -0.04352174976723523, 
                                0.0, 
                                -0.18543096144879875, 
                                0.009184538101484879, 
                                -0.9826143713563509, 
                                0.0, 
                                12.51456106373755, 
                                93.3237357513248, 
                                -67.6527607239772, 
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
                            "value": 52
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
                        "shapeIcon": "joint"
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
            "id": 20
        }, 
        "21": {
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
                        "angularDamping": 160.00001525878906, 
                        "angularStiffness": 1600.0001220703125, 
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
                                0.7693171234831949, 
                                0.6388670937805003, 
                                0.0, 
                                0.0, 
                                -0.6388670937805003, 
                                0.7693171234831949, 
                                0.0, 
                                -7.105427357601002e-15, 
                                42.71420669555665, 
                                -8.526512829121202e-14, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "strength": 0.4000000059604645
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 22
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -1.0, 
                                0.0, 
                                -5.66553889764798e-16, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                5.66553889764798e-16, 
                                0.0, 
                                -1.0, 
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
                            "value": 20
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -0.9999985577303054, 
                                -0.0006998791711230599, 
                                -0.0015474839110124977, 
                                0.0, 
                                -0.0015186768885457607, 
                                0.7763963810428312, 
                                0.6302430905008822, 
                                0.0, 
                                0.0007603668964463169, 
                                0.6302445316484235, 
                                -0.7763963241601817, 
                                0.0, 
                                7.105427357601002e-15, 
                                42.71420669555664, 
                                -5.684341886080802e-14, 
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
                        "path": "|_:pup_Tiger_|_:grp_Lf_HindLeg_|_:grpCtrlFk_Lf_HindLeg_|_:ctrlFK_Lf_HindLeg_1_|_:ctrlFK_Lf_HindLeg_2_", 
                        "shortestPath": "_:ctrlFK_Lf_HindLeg_2_", 
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
            "id": 21
        }, 
        "22": {
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
                                32.43294906616211, 
                                7.491072177886963, 
                                7.491072177886963
                            ]
                        }, 
                        "length": 32.43294906616211, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                2.1316282072803006e-14, 
                                16.216474533081055, 
                                -1.4210854715202004e-14
                            ]
                        }, 
                        "radius": 3.7455360889434814, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.5000000000000007, 
                                0.5000000000000001, 
                                0.4999999999999993, 
                                0.49999999999999983
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Lf_HindLeg_|_:grpCtrlFk_Lf_HindLeg_|_:ctrlFK_Lf_HindLeg_1_|_:ctrlFK_Lf_HindLeg_2_", 
                        "shortestPath": "_:ctrlFK_Lf_HindLeg_2_", 
                        "value": "rRigid1"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.9655007091712775, 
                                0.1862024062615811, 
                                -0.18203583298943482, 
                                0.0, 
                                0.0229472378097554, 
                                -0.7571809823524813, 
                                -0.6528019487108122, 
                                0.0, 
                                -0.259387364508495, 
                                0.6261035248791756, 
                                -0.7353316063295585, 
                                0.0, 
                                20.287237828210348, 
                                51.363836425467845, 
                                -69.51175777593178, 
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
                            "value": 20
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
                        "shapeIcon": "joint"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0000000000000002, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                1.0000000000000002, 
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
                        "angularDamping": 90.0, 
                        "angularStiffness": 900.0000610351562, 
                        "enabled": true, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                -0.0, 
                                0.0, 
                                -0.0, 
                                0.5739372799164539, 
                                -0.8188992604234675, 
                                0.0, 
                                0.0, 
                                0.8188992604234675, 
                                0.5739372799164539, 
                                0.0, 
                                3.552713678800501e-14, 
                                32.43294906616211, 
                                -2.842170943040401e-14, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "strength": 0.30000001192092896
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 24
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -1.0, 
                                0.0, 
                                -5.66553889764798e-16, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                5.66553889764798e-16, 
                                0.0, 
                                -1.0, 
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
                            "value": 22
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -0.9999941067619491, 
                                0.0034257515904801985, 
                                0.00022509422928994067, 
                                0.0, 
                                0.0023500133064705436, 
                                0.7308291062961522, 
                                -0.6825564407635656, 
                                0.0, 
                                -0.0025027742269626767, 
                                -0.682551889321543, 
                                -0.7308328499080765, 
                                0.0, 
                                3.552713678800501e-14, 
                                32.43294906616212, 
                                -2.842170943040401e-14, 
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
                        "twist": 1.0413981676101685, 
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
                        "path": "|_:pup_Tiger_|_:grp_Lf_HindLeg_|_:grpCtrlFk_Lf_HindLeg_|_:ctrlFK_Lf_HindLeg_1_|_:ctrlFK_Lf_HindLeg_2_|_:ctrlFK_Lf_HindLeg_3_", 
                        "shortestPath": "_:ctrlFK_Lf_HindLeg_3_", 
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
            "id": 23
        }, 
        "24": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.699999988079071, 
                                0.36516663432121277, 
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
                                19.880722045898438, 
                                7.491072177886963, 
                                7.491072177886963
                            ]
                        }, 
                        "length": 19.880722045898438, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                9.940361022949219, 
                                0.0
                            ]
                        }, 
                        "radius": 3.7455360889434814, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                -0.49999999999999983, 
                                -0.4999999999999996, 
                                0.5000000000000001, 
                                0.5000000000000003
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Lf_HindLeg_|_:grpCtrlFk_Lf_HindLeg_|_:ctrlFK_Lf_HindLeg_1_|_:ctrlFK_Lf_HindLeg_2_|_:ctrlFK_Lf_HindLeg_3_", 
                        "shortestPath": "_:ctrlFK_Lf_HindLeg_3_", 
                        "value": "rRigid2"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.9654747943082372, 
                                0.18865429059066655, 
                                -0.17963290399367057, 
                                0.0, 
                                0.22520509026210925, 
                                -0.9510584738013594, 
                                0.211590280331268, 
                                0.0, 
                                -0.13092398128495084, 
                                -0.24473932673839263, 
                                -0.9607088909092789, 
                                0.0, 
                                21.03148439085461, 
                                26.80622526165966, 
                                -90.68404920566229, 
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
                            "value": 22
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
                        "shapeIcon": "joint"
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
            "id": 24
        }, 
        "25": {
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
                        "angularDamping": 40.000003814697266, 
                        "angularStiffness": 400.0000305175781, 
                        "enabled": true, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                0.9805034775093399, 
                                0.1950962635986079, 
                                -0.023460147526260883, 
                                0.0, 
                                -0.1685191919483425, 
                                0.7734574689614074, 
                                -0.6110358628205803, 
                                0.0, 
                                -0.10106538743392382, 
                                0.6030762734826134, 
                                0.7912552027160106, 
                                0.0, 
                                0.0, 
                                19.880722045898445, 
                                -4.263256414560601e-14, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "strength": 0.20000000298023224
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
                                1.3322676295501878e-15, 
                                1.0000000000000002, 
                                0.0, 
                                0.0, 
                                -0.30779650846137707, 
                                3.3306690738754696e-16, 
                                -0.9514522107699291, 
                                0.0, 
                                -0.9514522107699291, 
                                1.4432899320127039e-15, 
                                0.30779650846137707, 
                                0.0, 
                                0.0, 
                                -1.4210854715202002e-14, 
                                7.105427357601002e-15, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 24
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -0.16851919194834086, 
                                0.7734574689614055, 
                                -0.6110358628205835, 
                                0.0, 
                                -0.20563666060528663, 
                                -0.6338482024174374, 
                                -0.7456205604107826, 
                                0.0, 
                                -0.9640097747223233, 
                                6.661338147750941e-16, 
                                0.2658667979267354, 
                                0.0, 
                                7.105427357601002e-15, 
                                19.880721131567796, 
                                -2.842170943040401e-14, 
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
                        "path": "|_:pup_Tiger_|_:grp_Lf_HindLeg_|_:grpCtrlFk_Lf_HindLeg_|_:ctrlFK_Lf_HindLeg_1_|_:ctrlFK_Lf_HindLeg_2_|_:ctrlFK_Lf_HindLeg_3_|_:ctrlFK_Lf_HindLeg_4_", 
                        "shortestPath": "_:ctrlFK_Lf_HindLeg_4_", 
                        "value": "rSocketConstraint21"
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
                                0.4713332951068878, 
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
                                9.575210571289062, 
                                7.491072177886963, 
                                7.491072177886963
                            ]
                        }, 
                        "length": 9.575210571289062, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                7.105427357601002e-15, 
                                4.787605285644531, 
                                -2.1316282072803006e-14
                            ]
                        }, 
                        "radius": 3.7455360889434814, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                -0.41599383755610614, 
                                -0.4159938375561057, 
                                0.5717946546753859, 
                                0.5717946546753865
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Lf_HindLeg_|_:grpCtrlFk_Lf_HindLeg_|_:ctrlFK_Lf_HindLeg_1_|_:ctrlFK_Lf_HindLeg_2_|_:ctrlFK_Lf_HindLeg_3_|_:ctrlFK_Lf_HindLeg_4_", 
                        "shortestPath": "_:ctrlFK_Lf_HindLeg_4_", 
                        "value": "rRigid3"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.9936130591358738, 
                                0.005666222393926675, 
                                -0.11269863636456753, 
                                0.0, 
                                0.09144815776682629, 
                                -0.6255500953217494, 
                                0.7748059838979076, 
                                0.0, 
                                -0.06610841970357563, 
                                -0.7801634265759536, 
                                -0.6220729094548025, 
                                0.0, 
                                25.50872398776517, 
                                7.898496964200369, 
                                -86.47748184824607, 
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
                            "value": 24
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
                        "shapeIcon": "joint"
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
            "id": 26
        }, 
        "27": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 3, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 35
                        }
                    }, 
                    "type": "ConstraintUIComponent"
                }, 
                "DriveComponent": {
                    "members": {
                        "acceleration": true, 
                        "angularDamping": 202.49998474121094, 
                        "angularStiffness": 2024.9998779296875, 
                        "enabled": true, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                0.9450166109366684, 
                                0.2228795004650403, 
                                -0.23930803021676378, 
                                0.0, 
                                0.0929645269131776, 
                                0.5184944229325943, 
                                0.8500124293935972, 
                                0.0, 
                                0.31353022468269703, 
                                -0.8255230230952072, 
                                0.46926595502994606, 
                                0.0, 
                                0.0001224123364238494, 
                                -36.499510264396655, 
                                -0.00012093155035586278, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "strength": 0.44999998807907104
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 28
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -0.968299792315028, 
                                -0.012461421718217973, 
                                -0.24947990935430917, 
                                0.0, 
                                0.022638831450278972, 
                                -0.9990225278784228, 
                                -0.0379667236138638, 
                                0.0, 
                                -0.2487629303438104, 
                                -0.042411104208289474, 
                                0.9676354182886208, 
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
                            "value": 36
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -0.9945526935771056, 
                                -0.026831372718115393, 
                                0.10072247582632844, 
                                0.0, 
                                -0.0737122366941787, 
                                -0.5021705576932847, 
                                -0.8616212840613657, 
                                0.0, 
                                0.07369834367246743, 
                                -0.8643522478851298, 
                                0.49745728029234626, 
                                0.0, 
                                0.00012241234071552753, 
                                -36.49951171874999, 
                                -0.00012093155237380415, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "JointComponent"
                }, 
                "LimitComponent": {
                    "members": {
                        "angularDamping": 30625.0, 
                        "angularStiffness": 306250.0, 
                        "enabled": true, 
                        "linearDamping": 30625.0, 
                        "linearStiffness": 3062500.0, 
                        "swing1": 0.12054670602083206, 
                        "swing2": 0.12054670602083206, 
                        "twist": 1.0793981552124023, 
                        "x": -1.0, 
                        "y": -1.0, 
                        "z": -1.0
                    }, 
                    "type": "LimitComponent"
                }, 
                "LimitUIComponent": {
                    "members": {
                        "angularDamping": 10000.0, 
                        "angularStiffness": 100000.0, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "strength": 1.75
                    }, 
                    "type": "LimitUIComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Rt_ForeLeg_|_:grpCtrlFk_Rt_ForeLeg_|_:ctrlFK_Rt_ForeLeg_1_", 
                        "shortestPath": "_:ctrlFK_Rt_ForeLeg_1_", 
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
            "id": 27
        }, 
        "28": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.699999988079071, 
                                0.6101666688919067, 
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
                                24.179468154907227, 
                                5.7937235832214355, 
                                5.7937235832214355
                            ]
                        }, 
                        "length": 24.179468154907227, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                -1.3891545677324757e-05, 
                                -12.089734077453613, 
                                1.9742201402550563e-05
                            ]
                        }, 
                        "radius": 2.8968617916107178, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                -0.4299279638056217, 
                                0.42992754106900766, 
                                -0.5613936978169558, 
                                0.5613923506957621
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Rt_ForeLeg_|_:grpCtrlFk_Rt_ForeLeg_|_:ctrlFK_Rt_ForeLeg_1_", 
                        "shortestPath": "_:ctrlFK_Rt_ForeLeg_1_", 
                        "value": "rRigid10"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.9479383694481675, 
                                -0.12370670447645438, 
                                -0.29344420082108413, 
                                0.0, 
                                0.2951560415931602, 
                                0.6872648429755053, 
                                0.6637393665595787, 
                                0.0, 
                                0.11956487293100022, 
                                -0.7157958416178661, 
                                0.6879974958410565, 
                                0.0, 
                                -13.371200000000023, 
                                70.85589999999993, 
                                38.26539999999997, 
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
                            "value": 36
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
                        "shapeIcon": "joint"
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
            "id": 28
        }, 
        "29": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 35
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
                                1.0, 
                                0.0, 
                                -0.0, 
                                0.0, 
                                -0.0, 
                                0.6179500757222849, 
                                -0.7862173388540998, 
                                0.0, 
                                0.0, 
                                0.7862173388540998, 
                                0.6179500757222849, 
                                0.0, 
                                -2.7783091354649514e-05, 
                                -24.179468154907248, 
                                3.948440281575927e-05, 
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
                            "value": 30
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                0.9898592262045911, 
                                0.0, 
                                -0.14205179441896568, 
                                0.0, 
                                1.7396327534832417e-17, 
                                -1.0, 
                                1.2122279329779282e-16, 
                                0.0, 
                                -0.14205179441896568, 
                                -1.2246467991473532e-16, 
                                -0.9898592262045911, 
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
                            "value": 28
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                0.9898592262045911, 
                                -0.11168358378752928, 
                                -0.08778091711768614, 
                                0.0, 
                                0.0427157984117714, 
                                -0.35532683135957543, 
                                0.9337656041437855, 
                                0.0, 
                                -0.13547720422157028, 
                                -0.9280461303342294, 
                                -0.3469528888883462, 
                                0.0, 
                                -2.7783091354649514e-05, 
                                -24.179468154907227, 
                                3.9484402805101126e-05, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "JointComponent"
                }, 
                "LimitComponent": {
                    "members": {
                        "angularDamping": 30625.0, 
                        "angularStiffness": 306250.0, 
                        "enabled": true, 
                        "linearDamping": 30625.0, 
                        "linearStiffness": 3062500.0, 
                        "swing1": 0.12054670602083206, 
                        "swing2": 0.12054670602083206, 
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
                        "angularStiffness": 100000.0, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "strength": 1.75
                    }, 
                    "type": "LimitUIComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Rt_ForeLeg_|_:grpCtrlFk_Rt_ForeLeg_|_:ctrlFK_Rt_ForeLeg_1_|_:ctrlFK_Rt_ForeLeg_2_", 
                        "shortestPath": "_:ctrlFK_Rt_ForeLeg_2_", 
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
            "id": 29
        }, 
        "30": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.4059999883174896, 
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
                                37.845420837402344, 
                                7.569084167480469, 
                                7.569084167480469
                            ]
                        }, 
                        "length": 37.845420837402344, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                -6.216770088940393e-06, 
                                -18.922710418701172, 
                                3.927078523702221e-06
                            ]
                        }, 
                        "radius": 3.7845420837402344, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.49999956516961047, 
                                -0.499999833203294, 
                                -0.5000003310640049, 
                                0.500000270562691
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Rt_ForeLeg_|_:grpCtrlFk_Rt_ForeLeg_|_:ctrlFK_Rt_ForeLeg_1_|_:ctrlFK_Rt_ForeLeg_2_", 
                        "shortestPath": "_:ctrlFK_Rt_ForeLeg_2_", 
                        "value": "rRigid11"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.9474431209487763, 
                                -0.1287710657572852, 
                                -0.29286438020110167, 
                                0.0, 
                                0.10414846687015249, 
                                0.9896983514754695, 
                                -0.098235787447014, 
                                0.0, 
                                0.30249732133597357, 
                                0.0625714448488374, 
                                0.9510942039956345, 
                                0.0, 
                                -20.5079378664947, 
                                54.23817645800155, 
                                22.21657012095098, 
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
                            "value": 28
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
                        "shapeIcon": "joint"
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
            "id": 30
        }, 
        "31": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 35
                        }
                    }, 
                    "type": "ConstraintUIComponent"
                }, 
                "DriveComponent": {
                    "members": {
                        "acceleration": true, 
                        "angularDamping": 250.0, 
                        "angularStiffness": 2500.0, 
                        "enabled": true, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                0.9971986099713049, 
                                0.04622222066883383, 
                                0.058808490779298644, 
                                0.0, 
                                -0.04886634946605168, 
                                0.997820333258342, 
                                0.04434706784076158, 
                                0.0, 
                                -0.05663048791206848, 
                                -0.047096590669102906, 
                                0.9972837605146231, 
                                0.0, 
                                -1.2433540184986214e-05, 
                                -37.845420837402344, 
                                7.85415705450987e-06, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "strength": 0.5
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 32
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -4.298625323917449e-06, 
                                -0.9999999999667486, 
                                -6.929993977167202e-06, 
                                0.0, 
                                0.7003658814534622, 
                                1.935908469308245e-06, 
                                -0.7137840234217682, 
                                0.0, 
                                0.7137840234114495, 
                                -7.921821419121232e-06, 
                                0.7003658814218523, 
                                0.0, 
                                0.0, 
                                3.552713678800501e-15, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 30
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                0.048862455330168975, 
                                -0.9978202055380816, 
                                -0.04435423180540871, 
                                0.0, 
                                0.7388257263661545, 
                                0.06599119198753867, 
                                -0.6706576687398631, 
                                0.0, 
                                0.6721227614942314, 
                                -6.715040701266163e-08, 
                                0.7404397298101744, 
                                0.0, 
                                -1.2433540376832752e-05, 
                                -37.84542046773666, 
                                7.854157281883545e-06, 
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
                        "path": "|_:pup_Tiger_|_:grp_Rt_ForeLeg_|_:grpCtrlFk_Rt_ForeLeg_|_:ctrlFK_Rt_ForeLeg_1_|_:ctrlFK_Rt_ForeLeg_2_|_:ctrlFK_Rt_ForeLeg_3_", 
                        "shortestPath": "_:ctrlFK_Rt_ForeLeg_3_", 
                        "value": "rSocketConstraint9"
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
            "id": 31
        }, 
        "32": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.38966667652130127, 
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
                                8.434833526611328, 
                                5.7937235832214355, 
                                5.7937235832214355
                            ]
                        }, 
                        "length": 8.434833526611328, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                -1.8129094314645045e-05, 
                                -4.217416763305664, 
                                -2.9226670449133962e-05
                            ]
                        }, 
                        "radius": 2.8968617916107178, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                -0.2736913791318401, 
                                0.2736970739302583, 
                                -0.6519908442874615, 
                                0.6519899383243959
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Rt_ForeLeg_|_:grpCtrlFk_Rt_ForeLeg_|_:ctrlFK_Rt_ForeLeg_1_|_:ctrlFK_Rt_ForeLeg_2_|_:ctrlFK_Rt_ForeLeg_3_", 
                        "shortestPath": "_:ctrlFK_Rt_ForeLeg_3_", 
                        "value": "rRigid12"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.9673916785816272, 
                                -0.07856406343179735, 
                                -0.24079250019073728, 
                                0.0, 
                                0.07065900610898075, 
                                0.9966450390200451, 
                                -0.04130340243156469, 
                                0.0, 
                                0.24322961387691405, 
                                0.02294240906742978, 
                                0.9696973758856265, 
                                0.0, 
                                -24.44948979047652, 
                                16.78262830271278, 
                                25.93435591324699, 
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
                            "value": 30
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
                        "shapeIcon": "joint"
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
            "id": 32
        }, 
        "33": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 35
                        }
                    }, 
                    "type": "ConstraintUIComponent"
                }, 
                "DriveComponent": {
                    "members": {
                        "acceleration": true, 
                        "angularDamping": 90.0, 
                        "angularStiffness": 900.0000610351562, 
                        "enabled": true, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                0.8986438112677322, 
                                0.05710135960298368, 
                                0.43494681882006586, 
                                0.0, 
                                0.27802403189539576, 
                                0.6928011755766532, 
                                -0.6653789663103542, 
                                0.0, 
                                -0.3393257110194163, 
                                0.7188643584509515, 
                                0.6067059386474385, 
                                0.0, 
                                -3.625818862929009e-05, 
                                -8.434833526611321, 
                                -5.84533408911625e-05, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "strength": 0.30000001192092896
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 34
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                3.4199147189717394e-06, 
                                -0.9999999999894243, 
                                -3.074978206230038e-06, 
                                0.0, 
                                0.07919599281048405, 
                                -2.7944763567600006e-06, 
                                0.9968590646199454, 
                                0.0, 
                                -0.996859064617996, 
                                -3.652698939649034e-06, 
                                0.07919599280008971, 
                                0.0, 
                                0.0, 
                                -3.552713678800501e-15, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 32
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -0.2780199151880922, 
                                -0.6928031907797813, 
                                0.6653785881768064, 
                                0.0, 
                                -0.26709169900355206, 
                                0.7211267148021148, 
                                0.6392482190214576, 
                                0.0, 
                                -0.9226954812299678, 
                                6.638039756590162e-06, 
                                -0.38552956938960525, 
                                0.0, 
                                -3.6258187186888335e-05, 
                                -8.434833103367739, 
                                -5.8453342607123204e-05, 
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
                        "path": "|_:pup_Tiger_|_:grp_Rt_ForeLeg_|_:grpCtrlFk_Rt_ForeLeg_|_:ctrlFK_Rt_ForeLeg_1_|_:ctrlFK_Rt_ForeLeg_2_|_:ctrlFK_Rt_ForeLeg_3_|_:ctrlFK_Rt_ForeLeg_4_", 
                        "shortestPath": "_:ctrlFK_Rt_ForeLeg_4_", 
                        "value": "rSocketConstraint10"
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
            "id": 33
        }, 
        "34": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.21000000834465027, 
                                0.699999988079071, 
                                0.6183332800865173, 
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
                                9.376784324645996, 
                                5.7937235832214355, 
                                5.7937235832214355
                            ]
                        }, 
                        "length": 9.376784324645996, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                1.6033900465117767e-05, 
                                -4.688392162322998, 
                                -1.4416703379538376e-05
                            ]
                        }, 
                        "radius": 2.8968617916107178, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.4797942844571482, 
                                -0.47979104639645853, 
                                -0.5194216416750765, 
                                0.5194219427013195
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Rt_ForeLeg_|_:grpCtrlFk_Rt_ForeLeg_|_:ctrlFK_Rt_ForeLeg_1_|_:ctrlFK_Rt_ForeLeg_2_|_:ctrlFK_Rt_ForeLeg_3_|_:ctrlFK_Rt_ForeLeg_4_", 
                        "shortestPath": "_:ctrlFK_Rt_ForeLeg_4_", 
                        "value": "rRigid13"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.9790870038734921, 
                                -0.0037438571787620353, 
                                0.20340752783378874, 
                                0.0, 
                                0.15537809567371205, 
                                0.659167976641941, 
                                -0.7357684594725301, 
                                0.0, 
                                -0.1313251165270349, 
                                0.751986410850086, 
                                0.6459645126986204, 
                                0.0, 
                                -25.045536007708133, 
                                8.37609524280929, 
                                26.282695268005074, 
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
                            "value": 32
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
                        "shapeIcon": "joint"
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
            "id": 34
        }, 
        "35": {
            "components": {
                "ConstraintMultiplierUIComponent": {
                    "members": {
                        "angularDriveDamping": 1.0, 
                        "angularDriveStiffness": 1.0, 
                        "angularLimitDamping": 1.0, 
                        "angularLimitStiffness": 1.0, 
                        "driveStrength": 1.0, 
                        "limitStrength": 1.0, 
                        "linearDriveDamping": 1.0, 
                        "linearDriveStiffness": 1.0, 
                        "linearLimitDamping": 1.0, 
                        "linearLimitStiffness": 1.0
                    }, 
                    "type": "ConstraintMultiplierUIComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Rt_ForeLeg_|_:grpFK_Rt_ForeClav_|_:ctrlFK_Rt_ForeClav_1_", 
                        "shortestPath": "_:ctrlFK_Rt_ForeClav_1_", 
                        "value": "rGuideMultiplier2"
                    }, 
                    "type": "NameComponent"
                }
            }, 
            "id": 35
        }, 
        "36": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.3923889100551605, 
                                0.3923889100551605, 
                                0.3923889100551605, 
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
                                36.49951171875, 
                                7.299901962280273, 
                                7.299901962280273
                            ]
                        }, 
                        "length": 36.49951171875, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                6.120617035776377e-05, 
                                -18.249755859375, 
                                -6.0465776186902076e-05
                            ]
                        }, 
                        "radius": 3.6499509811401367, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                -0.5264797209260071, 
                                0.5264795191863625, 
                                -0.47203563316075636, 
                                0.4720389606351302
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Rt_ForeLeg_|_:grpFK_Rt_ForeClav_|_:ctrlFK_Rt_ForeClav_1_", 
                        "shortestPath": "_:ctrlFK_Rt_ForeClav_1_", 
                        "value": "rRigid9"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.9569262095735861, 
                                -0.2903312408803593, 
                                6.938893903907228e-18, 
                                0.0, 
                                0.2797469793950507, 
                                0.9220406864257489, 
                                -0.2675492479804024, 
                                0.0, 
                                0.07767790516275719, 
                                0.25602488774414994, 
                                0.9635441867943167, 
                                0.0, 
                                -3.1606800000000077, 
                                104.50999999999995, 
                                28.50009999999999, 
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
                        "shaded": false, 
                        "shapeIcon": "joint"
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
            "id": 36
        }, 
        "37": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 3, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 45
                        }
                    }, 
                    "type": "ConstraintUIComponent"
                }, 
                "DriveComponent": {
                    "members": {
                        "acceleration": true, 
                        "angularDamping": 202.49998474121094, 
                        "angularStiffness": 2024.9998779296875, 
                        "enabled": true, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                0.9450166109366666, 
                                0.22287950046504662, 
                                -0.23930803021676536, 
                                0.0, 
                                0.0929645269131749, 
                                0.5184944229325965, 
                                0.8500124293935962, 
                                0.0, 
                                0.3135302246827036, 
                                -0.8255230230952042, 
                                0.4692659550299473, 
                                0.0, 
                                0.0, 
                                36.49924936015972, 
                                7.105427357601002e-15, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "strength": 0.44999998807907104
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 38
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -0.968299792315028, 
                                -0.012461421718217852, 
                                -0.24947990935430925, 
                                0.0, 
                                -0.012868318271322081, 
                                0.9999171997644944, 
                                0.0, 
                                0.0, 
                                0.2494592523590608, 
                                0.0032103868758718342, 
                                -0.9683799744049675, 
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
                            "value": 46
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -0.9952754172391161, 
                                -0.01690730122670732, 
                                0.09560850906029467, 
                                0.0, 
                                0.07169591931190553, 
                                0.5360427073044229, 
                                0.8411408390393166, 
                                0.0, 
                                -0.06547166557774287, 
                                0.8440215394828346, 
                                -0.5322979446658629, 
                                0.0, 
                                -7.105427357601002e-15, 
                                36.499248504638665, 
                                1.4210854715202002e-14, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "JointComponent"
                }, 
                "LimitComponent": {
                    "members": {
                        "angularDamping": 30625.0, 
                        "angularStiffness": 306250.0, 
                        "enabled": true, 
                        "linearDamping": 30625.0, 
                        "linearStiffness": 3062500.0, 
                        "swing1": 0.12054670602083206, 
                        "swing2": 0.12054670602083206, 
                        "twist": 1.0793981552124023, 
                        "x": -1.0, 
                        "y": -1.0, 
                        "z": -1.0
                    }, 
                    "type": "LimitComponent"
                }, 
                "LimitUIComponent": {
                    "members": {
                        "angularDamping": 10000.0, 
                        "angularStiffness": 100000.0, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "strength": 1.75
                    }, 
                    "type": "LimitUIComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Lf_ForeLeg_|_:grpCtrlFk_Lf_ForeLeg_|_:ctrlFK_Lf_ForeLeg_1_", 
                        "shortestPath": "_:ctrlFK_Lf_ForeLeg_1_", 
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
            "id": 37
        }, 
        "38": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.699999988079071, 
                                0.5774999856948853, 
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
                                24.179485321044922, 
                                5.793723106384277, 
                                5.793723106384277
                            ]
                        }, 
                        "length": 24.179485321044922, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                -1.4210854715202004e-14, 
                                12.089742660522461, 
                                1.0658141036401503e-14
                            ]
                        }, 
                        "radius": 2.8968615531921387, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.4299264233935136, 
                                0.4299264233935141, 
                                0.5613940420667656, 
                                0.5613940420667649
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Lf_ForeLeg_|_:grpCtrlFk_Lf_ForeLeg_|_:ctrlFK_Lf_ForeLeg_1_", 
                        "shortestPath": "_:ctrlFK_Lf_ForeLeg_1_", 
                        "value": "rRigid5"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.9489057833251406, 
                                0.1323903227168063, 
                                0.2864447884375647, 
                                0.0, 
                                0.2961374327061018, 
                                -0.6871438643336945, 
                                -0.66342741174811, 
                                0.0, 
                                0.10899740970472795, 
                                0.7143571320841537, 
                                -0.6912405171271157, 
                                0.0, 
                                13.371236203144306, 
                                70.85586139557842, 
                                38.26541449960123, 
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
                            "value": 46
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
                        "shapeIcon": "joint"
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
            "id": 38
        }, 
        "39": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 45
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
                                1.0, 
                                0.0, 
                                -0.0, 
                                0.0, 
                                -0.0, 
                                0.6179500757222852, 
                                -0.7862173388540996, 
                                0.0, 
                                0.0, 
                                0.7862173388540996, 
                                0.6179500757222852, 
                                0.0, 
                                -1.4210854715202004e-14, 
                                24.17948532104493, 
                                2.842170943040401e-14, 
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
                            "value": 40
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -0.9898592262045911, 
                                0.0, 
                                -0.14205179441896656, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.14205179441896656, 
                                0.0, 
                                -0.9898592262045911, 
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
                            "value": 38
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -0.9898592262045915, 
                                -0.11168358378752785, 
                                -0.08778091711768576, 
                                0.0, 
                                0.04974758692667396, 
                                0.3062696866178243, 
                                -0.9506440220471557, 
                                0.0, 
                                0.1330559652650748, 
                                -0.9453706448644332, 
                                -0.29760788621268985, 
                                0.0, 
                                -1.4210854715202004e-14, 
                                24.179485321044922, 
                                2.1316282072803006e-14, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "JointComponent"
                }, 
                "LimitComponent": {
                    "members": {
                        "angularDamping": 30625.0, 
                        "angularStiffness": 306250.0, 
                        "enabled": true, 
                        "linearDamping": 30625.0, 
                        "linearStiffness": 3062500.0, 
                        "swing1": 0.12054670602083206, 
                        "swing2": 0.12054670602083206, 
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
                        "angularStiffness": 100000.0, 
                        "linearDamping": 10000.0, 
                        "linearStiffness": 1000000.0, 
                        "strength": 1.75
                    }, 
                    "type": "LimitUIComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Lf_ForeLeg_|_:grpCtrlFk_Lf_ForeLeg_|_:ctrlFK_Lf_ForeLeg_1_|_:ctrlFK_Lf_ForeLeg_2_", 
                        "shortestPath": "_:ctrlFK_Lf_ForeLeg_2_", 
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
            "id": 39
        }, 
        "40": {
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
                                37.845375061035156, 
                                7.569075107574463, 
                                7.569075107574463
                            ]
                        }, 
                        "length": 37.845375061035156, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                7.105427357601002e-15, 
                                18.922687530517578, 
                                3.552713678800501e-15
                            ]
                        }, 
                        "radius": 3.7845375537872314, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                -0.5000000000000003, 
                                -0.5000000000000004, 
                                0.49999999999999967, 
                                0.4999999999999996
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Lf_ForeLeg_|_:grpCtrlFk_Lf_ForeLeg_|_:ctrlFK_Lf_ForeLeg_1_|_:ctrlFK_Lf_ForeLeg_2_", 
                        "shortestPath": "_:ctrlFK_Lf_ForeLeg_2_", 
                        "value": "rRigid6"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.9494227290411067, 
                                0.12730759542440173, 
                                0.28703529003834044, 
                                0.0, 
                                0.10312150871701155, 
                                -0.9898367134041521, 
                                0.09792464060283121, 
                                0.0, 
                                0.2965846186505036, 
                                -0.06337236735773091, 
                                -0.9529016250565492, 
                                0.0, 
                                20.53168713981635, 
                                54.241075881854755, 
                                22.2240806214211, 
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
                            "value": 38
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
                        "shapeIcon": "joint"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0000000000000002, 
                                1.0000000000000002, 
                                0.9999999999999999
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0000000000000002, 
                                1.0000000000000002, 
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
            "id": 40
        }, 
        "41": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 45
                        }
                    }, 
                    "type": "ConstraintUIComponent"
                }, 
                "DriveComponent": {
                    "members": {
                        "acceleration": true, 
                        "angularDamping": 250.0, 
                        "angularStiffness": 2500.0, 
                        "enabled": true, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                0.9971986099713052, 
                                0.04622222066883467, 
                                0.058808490779294946, 
                                0.0, 
                                -0.04886634946605243, 
                                0.9978203332583419, 
                                0.044347067840763, 
                                0.0, 
                                -0.056630487912064674, 
                                -0.047096590669104176, 
                                0.9972837605146232, 
                                0.0, 
                                -1.4210854715202004e-14, 
                                37.84537506103517, 
                                0.0, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "strength": 0.5
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 42
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -6.661338147750939e-16, 
                                1.0, 
                                -5.551115123125784e-17, 
                                0.0, 
                                -0.700450651113809, 
                                -4.440892098500626e-16, 
                                0.7137008374341739, 
                                0.0, 
                                0.7137008374341739, 
                                3.885780586188049e-16, 
                                0.7004506511138089, 
                                0.0, 
                                -3.552713678800502e-15, 
                                -1.776356839400251e-15, 
                                -3.5527136788005e-15, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 40
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -0.04886634946605306, 
                                0.997820333258342, 
                                0.04434706784076242, 
                                0.0, 
                                -0.7389056422913323, 
                                -0.0659892607642456, 
                                0.6705698093814112, 
                                0.0, 
                                0.6720346208938162, 
                                7.216449660063518e-16, 
                                0.7405197285151184, 
                                0.0, 
                                -1.4210854715202007e-14, 
                                37.84537614813481, 
                                -3.5527136788005005e-15, 
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
                        "path": "|_:pup_Tiger_|_:grp_Lf_ForeLeg_|_:grpCtrlFk_Lf_ForeLeg_|_:ctrlFK_Lf_ForeLeg_1_|_:ctrlFK_Lf_ForeLeg_2_|_:ctrlFK_Lf_ForeLeg_3_", 
                        "shortestPath": "_:ctrlFK_Lf_ForeLeg_3_", 
                        "value": "rSocketConstraint5"
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
            "id": 41
        }, 
        "42": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.46316662430763245, 
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
                                8.43484878540039, 
                                5.793723106384277, 
                                5.793723106384277
                            ]
                        }, 
                        "length": 8.43484878540039, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                4.217424392700195, 
                                -3.552713678800501e-15
                            ]
                        }, 
                        "radius": 2.8968615531921387, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.27365550829747093, 
                                0.27365550829747093, 
                                0.6520066432011662, 
                                0.6520066432011662
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Lf_ForeLeg_|_:grpCtrlFk_Lf_ForeLeg_|_:ctrlFK_Lf_ForeLeg_1_|_:ctrlFK_Lf_ForeLeg_2_|_:ctrlFK_Lf_ForeLeg_3_", 
                        "shortestPath": "_:ctrlFK_Lf_ForeLeg_3_", 
                        "value": "rRigid7"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.9687398879318675, 
                                0.07768564092390334, 
                                0.23560129609999017, 
                                0.0, 
                                0.0698419999320273, 
                                -0.9966957378744843, 
                                0.04146927957334293, 
                                0.0, 
                                0.23804437522287222, 
                                -0.023718079540294458, 
                                -0.9709646379388246, 
                                0.0, 
                                24.4343594261748, 
                                16.78033313784109, 
                                25.93007547920616, 
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
                            "value": 40
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
                        "shapeIcon": "joint"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0000000000000002, 
                                1.0000000000000002, 
                                0.9999999999999998
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0000000000000002, 
                                1.0000000000000002, 
                                0.9999999999999998
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
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 45
                        }
                    }, 
                    "type": "ConstraintUIComponent"
                }, 
                "DriveComponent": {
                    "members": {
                        "acceleration": true, 
                        "angularDamping": 90.0, 
                        "angularStiffness": 900.0000610351562, 
                        "enabled": true, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                0.8986438112677303, 
                                0.05710135960298453, 
                                0.43494681882006986, 
                                0.0, 
                                0.27802403189539837, 
                                0.6928011755766528, 
                                -0.6653789663103536, 
                                0.0, 
                                -0.3393257110194194, 
                                0.7188643584509521, 
                                0.6067059386474364, 
                                0.0, 
                                -1.0658141036401503e-14, 
                                8.434848785400392, 
                                -1.0658141036401503e-14, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "strength": 0.30000001192092896
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 44
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                -0.07918331844577897, 
                                0.0, 
                                -0.9968600714643528, 
                                0.0, 
                                -0.9968600714643528, 
                                0.0, 
                                0.07918331844577886, 
                                0.0, 
                                0.0, 
                                -3.552713678800502e-15, 
                                1.0658141036401506e-14, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 42
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                0.27802403189539837, 
                                0.6928011755766533, 
                                -0.6653789663103529, 
                                0.0, 
                                0.26710265345956963, 
                                -0.7211286508797217, 
                                -0.6392414578195392, 
                                0.0, 
                                -0.922691069753839, 
                                -3.885780586188049e-16, 
                                -0.38554012734930265, 
                                0.0, 
                                -7.105427357601003e-15, 
                                8.43484925029709, 
                                -3.5527136788005e-15, 
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
                        "path": "|_:pup_Tiger_|_:grp_Lf_ForeLeg_|_:grpCtrlFk_Lf_ForeLeg_|_:ctrlFK_Lf_ForeLeg_1_|_:ctrlFK_Lf_ForeLeg_2_|_:ctrlFK_Lf_ForeLeg_3_|_:ctrlFK_Lf_ForeLeg_4_", 
                        "shortestPath": "_:ctrlFK_Lf_ForeLeg_4_", 
                        "value": "rSocketConstraint6"
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
            "id": 43
        }, 
        "44": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.21000000834465027, 
                                0.5285000205039978, 
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
                                9.376816749572754, 
                                5.793723106384277, 
                                5.793723106384277
                            ]
                        }, 
                        "length": 9.376816749572754, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                7.105427357601002e-15, 
                                4.688408374786377, 
                                3.552713678800501e-15
                            ]
                        }, 
                        "radius": 2.8968615531921387, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                -0.47979596745758, 
                                -0.47979596745757985, 
                                0.5194187420679436, 
                                0.5194187420679437
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Lf_ForeLeg_|_:grpCtrlFk_Lf_ForeLeg_|_:ctrlFK_Lf_ForeLeg_1_|_:ctrlFK_Lf_ForeLeg_2_|_:ctrlFK_Lf_ForeLeg_3_|_:ctrlFK_Lf_ForeLeg_4_", 
                        "shortestPath": "_:ctrlFK_Lf_ForeLeg_4_", 
                        "value": "rRigid8"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.9780533326399768, 
                                0.0027419179713379506, 
                                -0.20833665159465664, 
                                0.0, 
                                0.15849523821825792, 
                                -0.6588394004627991, 
                                0.7353977861402338, 
                                0.0, 
                                -0.13524399422515063, 
                                -0.7522786227746057, 
                                -0.6448146522392071, 
                                0.0, 
                                25.023466166940707, 
                                8.373354840456193, 
                                26.279862600925732, 
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
                            "value": 42
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
                        "shapeIcon": "joint"
                    }, 
                    "type": "RigidUIComponent"
                }, 
                "ScaleComponent": {
                    "members": {
                        "absolute": {
                            "type": "Vector3", 
                            "values": [
                                1.0000000000000002, 
                                1.0000000000000002, 
                                1.0000000000000002
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0000000000000002, 
                                1.0000000000000002, 
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
            "id": 44
        }, 
        "45": {
            "components": {
                "ConstraintMultiplierUIComponent": {
                    "members": {
                        "angularDriveDamping": 1.0, 
                        "angularDriveStiffness": 1.0, 
                        "angularLimitDamping": 1.0, 
                        "angularLimitStiffness": 1.0, 
                        "driveStrength": 1.0, 
                        "limitStrength": 1.0, 
                        "linearDriveDamping": 1.0, 
                        "linearDriveStiffness": 1.0, 
                        "linearLimitDamping": 1.0, 
                        "linearLimitStiffness": 1.0
                    }, 
                    "type": "ConstraintMultiplierUIComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Lf_ForeLeg_|_:grpFK_Lf_ForeClav_|_:ctrlFK_Lf_ForeClav_1_", 
                        "shortestPath": "_:ctrlFK_Lf_ForeClav_1_", 
                        "value": "rGuideMultiplier1"
                    }, 
                    "type": "NameComponent"
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
                                0.5176110863685608, 
                                0.5176110863685608, 
                                0.5176110863685608, 
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
                                36.49924850463867, 
                                7.299849987030029, 
                                7.299849987030029
                            ]
                        }, 
                        "length": 36.49924850463867, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                -2.1316282072803006e-14, 
                                18.249624252319336, 
                                2.1316282072803006e-14
                            ]
                        }, 
                        "radius": 3.6499249935150146, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.5264789026590386, 
                                0.5264789026590388, 
                                0.4720380970376592, 
                                0.472038097037659
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Lf_ForeLeg_|_:grpFK_Lf_ForeClav_|_:ctrlFK_Lf_ForeClav_1_", 
                        "shortestPath": "_:ctrlFK_Lf_ForeClav_1_", 
                        "value": "rRigid4"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.956926209573586, 
                                0.2903312408803597, 
                                0.0, 
                                0.0, 
                                0.27974697939505094, 
                                -0.9220406864257482, 
                                0.26754924798040425, 
                                0.0, 
                                0.07767790516275785, 
                                -0.25602488774415166, 
                                -0.9635441867943162, 
                                0.0, 
                                3.1606814444528775, 
                                104.50965432964462, 
                                28.50006778144126, 
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
                        "shaded": false, 
                        "shapeIcon": "joint"
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
                                0.9999999999999999
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                0.9999999999999999, 
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
            "id": 46
        }, 
        "47": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.5611666440963745, 
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
                                28.805908203125, 
                                5.761181831359863, 
                                5.761181831359863
                            ]
                        }, 
                        "length": 28.805908203125, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                -2.522703319027611e-14, 
                                14.4029541015625, 
                                -2.842170943040401e-14
                            ]
                        }, 
                        "radius": 2.8805909156799316, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                -0.5000000000000001, 
                                -0.5000000000000009, 
                                0.5, 
                                0.4999999999999992
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Face_|_:ctrlFK_Jaw_1_", 
                        "shortestPath": "_:ctrlFK_Jaw_1_", 
                        "value": "rRigid25"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                -1.0, 
                                -1.2246467991473532e-16, 
                                6.162975822039155e-33, 
                                0.0, 
                                7.796849736302063e-17, 
                                -0.6366610962222359, 
                                0.7711437275612769, 
                                0.0, 
                                -9.443786976404764e-17, 
                                0.7711437275612769, 
                                0.6366610962222359, 
                                0.0, 
                                5.2073881657550635e-14, 
                                102.09461303843685, 
                                69.60521213482089, 
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
                            "value": 49
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
                        "shapeIcon": "joint"
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
            "id": 47
        }, 
        "48": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 5, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 50
                        }
                    }, 
                    "type": "ConstraintUIComponent"
                }, 
                "DriveComponent": {
                    "members": {
                        "acceleration": true, 
                        "angularDamping": 90.0, 
                        "angularStiffness": 900.0000610351562, 
                        "enabled": true, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                -0.0, 
                                0.0, 
                                -0.0, 
                                0.8997635170603323, 
                                -0.4363778332674807, 
                                0.0, 
                                0.0, 
                                0.4363778332674807, 
                                0.8997635170603323, 
                                0.0, 
                                -1.7753402304569552e-14, 
                                8.90211200714112, 
                                -2.6386706829070903, 
                                1.0
                            ]
                        }
                    }, 
                    "type": "DriveComponent"
                }, 
                "DriveUIComponent": {
                    "members": {
                        "angularDamping": 1000.0, 
                        "angularStiffness": 10000.0, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "strength": 0.30000001192092896
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 47
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -1.5543122344752192e-15, 
                                1.0, 
                                0.0, 
                                0.0, 
                                1.77635683940025e-15, 
                                0.0, 
                                -1.0, 
                                0.0, 
                                -1.0, 
                                -1.5543122344752188e-15, 
                                -1.7763568394002505e-15, 
                                0.0, 
                                -1.262177448353619e-29, 
                                -4.440892098500626e-15, 
                                -1.4210854715202004e-14, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 49
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -1.5543122344752192e-15, 
                                0.8997635170603318, 
                                -0.43637783326748136, 
                                0.0, 
                                1.831867990631508e-15, 
                                -0.43637783326748125, 
                                -0.8997635170603318, 
                                0.0, 
                                -1.0, 
                                -2.164934898019055e-15, 
                                -8.881784197001252e-16, 
                                0.0, 
                                -1.775340263971832e-14, 
                                8.902111578924178, 
                                -2.6386706997039084, 
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
                        "path": "|_:pup_Tiger_|_:grp_Face_|_:ctrlFK_Jaw_1_", 
                        "shortestPath": "_:ctrlFK_Jaw_1_", 
                        "value": "rSocketConstraint20"
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
            "id": 48
        }, 
        "49": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.3896666467189789, 
                                0.3896666467189789, 
                                0.3896666467189789, 
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
                                9.284943580627441, 
                                8.054978370666504, 
                                8.054978370666504
                            ]
                        }, 
                        "length": 9.284943580627441, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                -7.97117126266015e-15, 
                                4.451056003570557, 
                                -1.3193353414535522
                            ]
                        }, 
                        "radius": 4.027489185333252, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                -0.5666101239550733, 
                                -0.42302832934877643, 
                                0.5666101239550736, 
                                0.4230283293487749
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Head_|_:grpCtrlFk_Head_|_:ctrlFK_Head_1_", 
                        "shortestPath": "_:ctrlFK_Head_1_", 
                        "value": "rRigid24"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                -1.0, 
                                -1.2246467991473532e-16, 
                                0.0, 
                                0.0, 
                                2.566842960764745e-17, 
                                -0.20959863387156874, 
                                0.977787508960496, 
                                0.0, 
                                -1.1974443430947355e-16, 
                                0.977787508960496, 
                                0.20959863387156863, 
                                0.0, 
                                3.3776009663144246e-14, 
                                106.54054271438217, 
                                61.45390040347112, 
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
                        "shaded": false, 
                        "shapeIcon": "joint"
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
            "id": 49
        }, 
        "50": {
            "components": {
                "ConstraintMultiplierUIComponent": {
                    "members": {
                        "angularDriveDamping": 1.0, 
                        "angularDriveStiffness": 1.0, 
                        "angularLimitDamping": 1.0, 
                        "angularLimitStiffness": 1.0, 
                        "driveStrength": 1.0, 
                        "limitStrength": 1.0, 
                        "linearDriveDamping": 1.0, 
                        "linearDriveStiffness": 1.0, 
                        "linearLimitDamping": 1.0, 
                        "linearLimitStiffness": 1.0
                    }, 
                    "type": "ConstraintMultiplierUIComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Head_|_:grpCtrlFk_Head_|_:ctrlFK_Head_1_", 
                        "shortestPath": "_:ctrlFK_Head_1_", 
                        "value": "rGuideMultiplier4"
                    }, 
                    "type": "NameComponent"
                }
            }, 
            "id": 50
        }, 
        "51": {
            "components": {
                "ConstraintMultiplierUIComponent": {
                    "members": {
                        "angularDriveDamping": 1.0, 
                        "angularDriveStiffness": 1.0, 
                        "angularLimitDamping": 1.0, 
                        "angularLimitStiffness": 1.0, 
                        "driveStrength": 1.0, 
                        "limitStrength": 1.0, 
                        "linearDriveDamping": 1.0, 
                        "linearDriveStiffness": 1.0, 
                        "linearLimitDamping": 1.0, 
                        "linearLimitStiffness": 1.0
                    }, 
                    "type": "ConstraintMultiplierUIComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:pup_Tiger_|_:grp_Spine_|_:grpIK_Hips_|_:ctrlIK_Hips_", 
                        "shortestPath": "_:ctrlIK_Hips_", 
                        "value": "rGuideMultiplier3"
                    }, 
                    "type": "NameComponent"
                }
            }, 
            "id": 51
        }, 
        "52": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.48766669631004333, 
                                0.48766669631004333, 
                                0.48766669631004333, 
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
                                17.91229820251465, 
                                20.030643463134766, 
                                20.030643463134766
                            ]
                        }, 
                        "length": 8.722298622131348, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.0, 
                                -6.5200000000000005, 
                                0.0
                            ]
                        }, 
                        "radius": 15.535321235656738, 
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
                        "path": "|_:pup_Tiger_|_:grp_Spine_|_:grpIK_Hips_|_:ctrlIK_Hips_", 
                        "shortestPath": "_:ctrlIK_Hips_", 
                        "value": "rRigid14"
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
                                -6.900461425499565e-14, 
                                98.48904710333548, 
                                -55.92444081762274, 
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
                        "shaded": false, 
                        "shapeIcon": "nurbsCurve"
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
            "id": 52
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
                                -982.0, 
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
        "entitiesCount": 53, 
        "mayaVersion": "20200200", 
        "ragdollVersion": "2021.03.29", 
        "registryAlive": 53, 
        "registrySize": 53, 
        "serialisationTimeMs": 2.1528, 
        "timestamp": 1618070965
    }, 
    "schema": "ragdoll-1.0", 
    "ui": {
        "description": "", 
        "filename": "C:/Users/marcus/Documents/maya/projects/default/scenes/demo/mytiger.rag", 
        "thumbnail": "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"
    }
}
```