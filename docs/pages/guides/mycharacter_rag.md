---
title: mytiger.rag
hide:
  - navigation # Hide navigation
  - toc        # Hide table of contents
---

<div class="vboxlayout align-center justify-center" markdown=1>

![image](https://user-images.githubusercontent.com/2152766/114277250-5fb20580-9a22-11eb-8d3a-520ae4ef8f94.png)

An "Advanced Skeleton" rig.

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
                                0.699999988079071, 
                                0.24266667664051056, 
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
                        "path": "|pCube1", 
                        "shortestPath": "pCube1", 
                        "value": "rRigid20"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.9494359965145187, 
                                0.22101342735761856, 
                                -0.22298958148335424, 
                                0.0, 
                                -0.10291339242723332, 
                                0.8900875784203919, 
                                0.4440190721138464, 
                                0.0, 
                                0.2966144335355262, 
                                -0.3986190758974807, 
                                0.867826428584102, 
                                0.0, 
                                -4.548418332161994, 
                                20.551354133626294, 
                                -8.307811023177798, 
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
            "id": 1
        }, 
        "2": {
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
                        "angularDamping": 0.0, 
                        "angularStiffness": 0.0, 
                        "enabled": true, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                0.9494359965145185, 
                                0.22101342735761897, 
                                -0.22298958148335468, 
                                0.0, 
                                -0.10291339242723332, 
                                0.8900875784203915, 
                                0.44401907211384695, 
                                0.0, 
                                0.29661443353552686, 
                                -0.39861907589748113, 
                                0.8678264285841015, 
                                0.0, 
                                -4.5484185218811035, 
                                20.551353454589844, 
                                -8.30781078338623, 
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
                        "linearDamping": 100.0, 
                        "linearStiffness": 1000.0, 
                        "strength": 0.0
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 1
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
                        "path": "|pCube1", 
                        "shortestPath": "pCube1", 
                        "value": "rAnimConstraint"
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
            "id": 2
        }, 
        "3": {
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
                                3.7872607707977295, 
                                1.2883373498916626, 
                                1.2883373498916626
                            ]
                        }, 
                        "length": 3.7872607707977295, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                1.8936303853988647, 
                                0.0, 
                                0.0
                            ]
                        }, 
                        "radius": 0.6441686749458313, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                -0.7071067811865477, 
                                0.0, 
                                0.0, 
                                0.7071067811865474
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|joint1|joint2", 
                        "shortestPath": "joint2", 
                        "value": "rRigid19"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.25050201169183783, 
                                0.7528241360809196, 
                                0.6086908593632402, 
                                0.0, 
                                0.4501930132076487, 
                                0.4660381041116023, 
                                -0.7616657642135962, 
                                0.0, 
                                -0.8570735050142202, 
                                0.46482717826099706, 
                                -0.2221726836327076, 
                                0.0, 
                                -6.548480707440984, 
                                20.698178791306077, 
                                -16.592988991525946, 
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
                            "value": 5
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
                                0.9999999999999999, 
                                0.9999999999999998
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                0.9999999999999999, 
                                0.9999999999999999, 
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
            "id": 3
        }, 
        "4": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 6
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
                                0.5389585308641575, 
                                0.0, 
                                -0.8423322990416248, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                0.8423322990416248, 
                                0.0, 
                                0.5389585308641575, 
                                0.0, 
                                8.141989707946784, 
                                7.105427357601002e-15, 
                                4.440892098500626e-15, 
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
                            "value": 3
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                -0.0, 
                                0.0, 
                                -0.0, 
                                -1.9984014443252818e-15, 
                                -1.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                -1.9984014443252818e-15, 
                                0.0, 
                                -2.2204460492503127e-15, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 5
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                0.5389585308641571, 
                                0.0, 
                                -0.8423322990416249, 
                                0.0, 
                                -0.8423322990416249, 
                                -1.1102230246251565e-15, 
                                -0.5389585308641571, 
                                0.0, 
                                -8.881784197001252e-16, 
                                1.0, 
                                -4.440892098500626e-16, 
                                0.0, 
                                8.141989231226376, 
                                7.105427357601001e-15, 
                                2.664535259100375e-15, 
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
                        "path": "|joint1|joint2", 
                        "shortestPath": "joint2", 
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
            "id": 4
        }, 
        "5": {
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
                                8.141989707946777, 
                                1.7388265132904053, 
                                1.7388265132904053
                            ]
                        }, 
                        "length": 8.141989707946777, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                4.070994853973389, 
                                3.552713678800501e-15, 
                                -8.881784197001252e-16
                            ]
                        }, 
                        "radius": 0.8694132566452026, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                -0.7071067811865469, 
                                0.0, 
                                0.0, 
                                0.7071067811865481
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|joint1", 
                        "shortestPath": "joint1", 
                        "value": "rRigid15"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                -0.5869304997263425, 
                                0.7972799361028672, 
                                0.1409159039242673, 
                                0.0, 
                                0.4501930132076486, 
                                0.46603810411160274, 
                                -0.7616657642135957, 
                                0.0, 
                                -0.6729330125279955, 
                                -0.38360551221778705, 
                                -0.6324618341418915, 
                                0.0, 
                                -1.7696988991908125, 
                                14.206734137283668, 
                                -17.740324763785807, 
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
                                0.9999999999999998, 
                                0.9999999999999999, 
                                0.9999999999999998
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                0.9999999999999998, 
                                0.9999999999999999, 
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
            "id": 5
        }, 
        "6": {
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
                        "path": "|joint1", 
                        "shortestPath": "joint1", 
                        "value": "rGuideMultiplier1"
                    }, 
                    "type": "NameComponent"
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
                                0.21816666424274445, 
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
                                2.4528188705444336, 
                                2.0, 
                                2.4528188705444336
                            ]
                        }, 
                        "length": 2.4528188705444336, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                -3.3306690738754696e-16, 
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
                                0.0, 
                                1.0
                            ]
                        }, 
                        "type": "Sphere"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|nurbsSphere1", 
                        "shortestPath": "nurbsSphere1", 
                        "value": "rRigid21"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                0.9485427773101404, 
                                0.2515500324739547, 
                                -0.19232571532459677, 
                                0.0, 
                                -0.09010724482276125, 
                                0.7966968112573096, 
                                0.5976243597468947, 
                                0.0, 
                                0.30355771122344505, 
                                -0.5495423296660478, 
                                0.7783674863854454, 
                                0.0, 
                                -0.15575818405004682, 
                                20.04056508016481, 
                                -5.729009249252099, 
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
                        "shapeIcon": "nurbsSurface"
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
                        "angularDamping": 0.0, 
                        "angularStiffness": 0.0, 
                        "enabled": true, 
                        "linearDamping": 0.0, 
                        "linearStiffness": 0.0, 
                        "target": {
                            "type": "Matrix44", 
                            "values": [
                                0.9485427773101403, 
                                0.25155003247395485, 
                                -0.1923257153245969, 
                                0.0, 
                                -0.0901072448227614, 
                                0.7966968112573097, 
                                0.5976243597468944, 
                                0.0, 
                                0.30355771122344527, 
                                -0.5495423296660475, 
                                0.7783674863854455, 
                                0.0, 
                                -0.15575818717479706, 
                                20.040565490722656, 
                                -5.72900915145874, 
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
                        "linearDamping": 100.0, 
                        "linearStiffness": 1000.0, 
                        "strength": 0.0
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
                        "path": "|nurbsSphere1", 
                        "shortestPath": "nurbsSphere1", 
                        "value": "rAnimConstraint1"
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
                                2.6142518520355225, 
                                1.0804892778396606, 
                                1.0804892778396606
                            ]
                        }, 
                        "length": 2.6142518520355225, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                -1.3071259260177612, 
                                -1.0130785099704553e-15, 
                                1.4210854715202004e-14
                            ]
                        }, 
                        "radius": 0.5402446389198303, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                2.958123450100391e-17, 
                                0.999998096339961, 
                                -0.0019512345974454692, 
                                1.516023661486793e-14
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToScapula_L|_:FKOffsetShoulder_L|_:FKExtraShoulder_L|_:FKShoulder_L", 
                        "shortestPath": "_:FKShoulder_L", 
                        "value": "rRigid5"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                -0.9986277024879406, 
                                4.890532423473813e-14, 
                                0.05237090627110352, 
                                0.0, 
                                -0.05237090586174294, 
                                -0.00012503251510920244, 
                                -0.9986276946821023, 
                                0.0, 
                                6.548066080788726e-06, 
                                -0.9999999921834349, 
                                0.00012486093330255077, 
                                0.0, 
                                1.5290766965528109, 
                                13.706785158269431, 
                                -0.16734312260574308, 
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
                            "value": 19
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
                                1.0000000000000004, 
                                1.0, 
                                1.0000000000000002
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0000000000000004, 
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
            "id": 9
        }, 
        "10": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 18
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
                                0.9986440815011526, 
                                -0.05205724936633906, 
                                0.00020315297218703387, 
                                0.0, 
                                0.05205724936633898, 
                                0.9986441021507172, 
                                5.2913802452127155e-06, 
                                0.0, 
                                -0.00020315297220988723, 
                                5.291379367799553e-06, 
                                0.9999999793504354, 
                                0.0, 
                                -1.0925408230395592, 
                                1.3541112675596878e-12, 
                                2.6645352591003757e-14, 
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
                            "value": 9
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -1.0, 
                                -1.232595164407831e-32, 
                                -3.209688778911925e-14, 
                                0.0, 
                                1.2525687740393844e-16, 
                                0.9999923853670912, 
                                -0.0039024617659784502, 
                                0.0, 
                                3.209664338310122e-14, 
                                -0.0039024617659784502, 
                                -0.9999923853670911, 
                                0.0, 
                                2.220446049250314e-16, 
                                0.0, 
                                1.776356839400251e-15, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 19
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -0.9986440815011526, 
                                0.052057249366338494, 
                                -0.0002031529722189908, 
                                0.0, 
                                0.052057645766201054, 
                                0.9986364771930671, 
                                -0.003897170345440804, 
                                0.0, 
                                1.2362533956603031e-14, 
                                -0.0039024617655403888, 
                                -0.9999923853670929, 
                                0.0, 
                                -1.0925408230395586, 
                                1.3543333121646128e-12, 
                                3.019806626980426e-14, 
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
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToScapula_L|_:FKOffsetShoulder_L|_:FKExtraShoulder_L|_:FKShoulder_L", 
                        "shortestPath": "_:FKShoulder_L", 
                        "value": "rSocketConstraint4"
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
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.21000000834465027, 
                                0.699999988079071, 
                                0.6836666464805603, 
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
                                2.2826035022735596, 
                                0.7480310797691345, 
                                0.7480310797691345
                            ]
                        }, 
                        "length": 2.2826035022735596, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                -1.1413017511367798, 
                                -3.9968028886505635e-15, 
                                -2.8421709430404007e-13
                            ]
                        }, 
                        "radius": 0.37401553988456726, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                9.71678845008606e-21, 
                                -5.287791503802194e-06, 
                                -0.9999999999860196, 
                                1.837589179331928e-15
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToScapula_L|_:FKOffsetShoulder_L|_:FKExtraShoulder_L|_:FKShoulder_L|_:FKXShoulder_L|_:FKOffsetElbow_L|_:FKExtraElbow_L|_:FKElbow_L", 
                        "shortestPath": "_:FKElbow_L", 
                        "value": "rRigid6"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                -0.9982602798557889, 
                                -1.272303256852694e-05, 
                                -0.05896111854744928, 
                                0.0, 
                                0.05896111967557846, 
                                -0.00012432317085742106, 
                                -0.9982602721286424, 
                                0.0, 
                                5.370664739039187e-06, 
                                -0.9999999921909368, 
                                0.00012485704757858596, 
                                0.0, 
                                4.139741069445527, 
                                13.706785158269206, 
                                -0.30425386405367544, 
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
                            "value": 9
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
            "id": 11
        }, 
        "12": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 18
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
                                0.9938025225442675, 
                                0.11116000262355466, 
                                -1.1755820974364542e-06, 
                                0.0, 
                                -0.11116000262355466, 
                                0.9938025225449606, 
                                6.554193659403703e-08, 
                                0.0, 
                                1.17558209573479e-06, 
                                6.554196711564971e-08, 
                                0.9999999999993069, 
                                0.0, 
                                -2.614251904276842, 
                                -1.6930901125533637e-15, 
                                3.019806626980426e-14, 
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
                            "value": 11
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -1.0, 
                                -4.119267568565298e-15, 
                                -3.009265538105056e-36, 
                                0.0, 
                                4.119267568334943e-15, 
                                -0.9999999999440785, 
                                1.0575583013357995e-05, 
                                0.0, 
                                -4.3563656125595666e-20, 
                                1.0575583013357995e-05, 
                                0.9999999999440785, 
                                0.0, 
                                0.0, 
                                0.0, 
                                -1.776356839400251e-15, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 9
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -0.9938025225442675, 
                                -0.11116000262355855, 
                                1.1755818450345697e-06, 
                                0.0, 
                                0.11116000262977477, 
                                -0.9938025224886924, 
                                1.0510041076759093e-05, 
                                0.0, 
                                9.321017684602063e-15, 
                                1.057558301511261e-05, 
                                0.9999999999440785, 
                                0.0, 
                                -2.6142519042768435, 
                                -1.8596235662471372e-15, 
                                3.1974423109204515e-14, 
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
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToScapula_L|_:FKOffsetShoulder_L|_:FKExtraShoulder_L|_:FKShoulder_L|_:FKXShoulder_L|_:FKOffsetElbow_L|_:FKExtraElbow_L|_:FKElbow_L", 
                        "shortestPath": "_:FKElbow_L", 
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
            "id": 12
        }, 
        "13": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.34066668152809143, 
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
                                2.2826035022735596, 
                                0.7480310797691345, 
                                0.7480310797691345
                            ]
                        }, 
                        "length": 2.2826035022735596, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                -1.1413017511367798, 
                                -3.9968028886505635e-15, 
                                -2.8421709430404007e-13
                            ]
                        }, 
                        "radius": 0.37401553988456726, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                9.71678845008606e-21, 
                                -5.287791503802194e-06, 
                                -0.9999999999860196, 
                                1.837589179331928e-15
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToScapula_L|_:FKOffsetShoulder_L|_:FKExtraShoulder_L|_:FKShoulder_L|_:FKXShoulder_L|_:FKOffsetElbow_L|_:FKExtraElbow_L|_:FKElbow_L|_:FKXElbow_L|_:FKOffsetWrist_L|_:FKExtraWrist_L|_:FKWrist_L", 
                        "shortestPath": "_:FKWrist_L", 
                        "value": "rRigid7"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                -0.9999915252214038, 
                                -6.464731455679308e-06, 
                                -0.004116970193950224, 
                                0.0, 
                                0.0041169709059011746, 
                                -0.00011427421419685224, 
                                -0.9999915187100159, 
                                0.0, 
                                5.994213092631699e-06, 
                                -0.9999999934498056, 
                                0.00011429986085942367, 
                                0.0, 
                                6.418373455819859, 
                                13.706814199908171, 
                                -0.16966900981256394, 
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
                            "value": 11
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
                                1.0000000000000007, 
                                1.0000000000000002, 
                                1.0000000000000002
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0000000000000007, 
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
            "id": 13
        }, 
        "14": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 18
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
                                0.9984945610708486, 
                                -0.05485081140326919, 
                                5.800794370436475e-07, 
                                0.0, 
                                0.054850811406336526, 
                                0.9984945610150112, 
                                -1.0559664454785628e-05, 
                                0.0, 
                                6.465201316067102e-16, 
                                1.0575585352638593e-05, 
                                0.9999999999440785, 
                                0.0, 
                                -2.282603477625604, 
                                -8.881784197001252e-15, 
                                -5.702105454474804e-13, 
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
                            "value": 13
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -0.9999915252214038, 
                                0.004116970905901106, 
                                5.994213092822083e-06, 
                                0.0, 
                                -6.464731454393443e-06, 
                                -0.00011427421383847225, 
                                -0.9999999934498056, 
                                0.0, 
                                -0.0041169701939501565, 
                                -0.9999915187100159, 
                                0.00011429986050104368, 
                                0.0, 
                                0.0, 
                                -2.775557561562892e-17, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 11
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -0.9982602798557889, 
                                0.058961119675578294, 
                                5.370664739486747e-06, 
                                0.0, 
                                -1.2723032547852509e-05, 
                                -0.0001243231704997072, 
                                -0.9999999921909369, 
                                0.0, 
                                -0.05896111854744912, 
                                -0.9982602721286425, 
                                0.00012485704722031699, 
                                0.0, 
                                -2.2826034776256043, 
                                -8.881784197001254e-15, 
                                -5.73763259126281e-13, 
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
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToScapula_L|_:FKOffsetShoulder_L|_:FKExtraShoulder_L|_:FKShoulder_L|_:FKXShoulder_L|_:FKOffsetElbow_L|_:FKExtraElbow_L|_:FKElbow_L|_:FKXElbow_L|_:FKOffsetWrist_L|_:FKExtraWrist_L|_:FKWrist_L", 
                        "shortestPath": "_:FKWrist_L", 
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
                                0.3814999759197235, 
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
                                2.577422857284546, 
                                1.83683180809021, 
                                1.83683180809021
                            ]
                        }, 
                        "length": 2.577422857284546, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                1.282149076461792, 
                                0.12988707423210144, 
                                1.0595095738862655e-15
                            ]
                        }, 
                        "radius": 0.918415904045105, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                0.0, 
                                0.05045844414385831, 
                                0.9987261613748691
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKOffsetRoot_M|_:FKExtraRoot_M|_:FKXRoot_M|_:FKOffsetRootPart1_M|_:FKExtraRootPart1_M|_:FKRootPart1_M|_:FKXRootPart1_M|_:FKOffsetRootPart2_M|_:FKExtraRootPart2_M|_:FKRootPart2_M|_:FKXRootPart2_M|_:HipSwingerStabilizer|_:FKOffsetSpine1_M|_:FKExtraSpine1_M|_:FKSpine1_M", 
                        "shortestPath": "_:FKSpine1_M", 
                        "value": "rRigid1"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                3.3306690738754696e-16, 
                                0.9963049309234995, 
                                -0.08588646352901595, 
                                0.0, 
                                -3.3306690738754686e-16, 
                                0.08588646352901597, 
                                0.9963049309234995, 
                                0.0, 
                                1.0, 
                                -3.3306690738754686e-16, 
                                3.3306690738754696e-16, 
                                0.0, 
                                -9.929571208637703e-16, 
                                11.567432593163515, 
                                -0.4225900827926008, 
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
                            "value": 17
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
            "id": 15
        }, 
        "16": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 1, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 18
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
                                0.9985307901596494, 
                                0.054187278056257275, 
                                0.0, 
                                0.0, 
                                -0.054187278056257275, 
                                0.9985307901596494, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                1.7561552005093581, 
                                2.220446049250313e-16, 
                                -1.7749691236235465e-15, 
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
                            "value": 15
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                0.9949078908291623, 
                                0.10078833645748773, 
                                0.0, 
                                0.0, 
                                -0.10078833645748773, 
                                0.9949078908291623, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                1.7763568394002505e-15, 
                                0.0, 
                                -7.888609052210117e-31, 
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
                                0.9879847167532642, 
                                0.15455160776249605, 
                                0.0, 
                                0.0, 
                                -0.15455160776249605, 
                                0.9879847167532642, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                1.7561552005093617, 
                                2.220446049250313e-16, 
                                -1.774969123623548e-15, 
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
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKOffsetRoot_M|_:FKExtraRoot_M|_:FKXRoot_M|_:FKOffsetRootPart1_M|_:FKExtraRootPart1_M|_:FKRootPart1_M|_:FKXRootPart1_M|_:FKOffsetRootPart2_M|_:FKExtraRootPart2_M|_:FKRootPart2_M|_:FKXRootPart2_M|_:HipSwingerStabilizer|_:FKOffsetSpine1_M|_:FKExtraSpine1_M|_:FKSpine1_M", 
                        "shortestPath": "_:FKSpine1_M", 
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
            "id": 16
        }, 
        "17": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.40872225165367126, 
                                0.40872225165367126, 
                                0.40872225165367126, 
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
                                1.756155252456665, 
                                1.83683180809021, 
                                1.83683180809021
                            ]
                        }, 
                        "length": 1.756155252456665, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.8780776262283325, 
                                2.220446049250313e-16, 
                                -7.993395395492853e-16
                            ]
                        }, 
                        "radius": 0.918415904045105, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                -0.6558401746567458, 
                                0.0, 
                                0.0, 
                                0.7548997716956928
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKOffsetRoot_M|_:FKExtraRoot_M|_:FKRoot_M", 
                        "shortestPath": "_:FKRoot_M", 
                        "value": "rRigid"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                4.440892098500626e-16, 
                                0.9901871962344814, 
                                -0.139747330612418, 
                                0.0, 
                                -3.330669073875468e-16, 
                                0.13974733061241806, 
                                0.9901871962344814, 
                                0.0, 
                                1.0, 
                                -3.330669073875468e-16, 
                                4.440892098500626e-16, 
                                0.0, 
                                1.9709482123357003e-16, 
                                9.82851019901844, 
                                -0.17717208138029264, 
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
            "id": 17
        }, 
        "18": {
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
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKOffsetRoot_M|_:FKExtraRoot_M|_:FKRoot_M", 
                        "shortestPath": "_:FKRoot_M", 
                        "value": "rGuideMultiplier"
                    }, 
                    "type": "NameComponent"
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
                                0.6264999508857727, 
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
                                1.0925408601760864, 
                                0.5395034551620483, 
                                0.5395034551620483
                            ]
                        }, 
                        "length": 1.0925408601760864, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                -0.5462704300880432, 
                                7.074063557155341e-13, 
                                1.0658141036401503e-14
                            ]
                        }, 
                        "radius": 0.26975172758102417, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                4.843179514678852e-13, 
                                0.7479313757744033, 
                                0.6637760594750374, 
                                4.2982374021349e-13
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToChest_M|_:FKOffsetScapula_L|_:FKExtraScapula_L|_:FKScapula_L", 
                        "shortestPath": "_:FKScapula_L", 
                        "value": "rRigid4"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                -0.999999931348921, 
                                0.0001966441218543524, 
                                0.0003140592984211835, 
                                0.0, 
                                -0.0003140848959228453, 
                                -0.00013015436276186954, 
                                -0.9999999422052583, 
                                0.0, 
                                -0.00019660323430150076, 
                                -0.9999999721954653, 
                                0.00013021611677488387, 
                                0.0, 
                                0.43653594851735356, 
                                13.707000000000205, 
                                -0.16700000000000872, 
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
                            "value": 15
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
            "id": 19
        }, 
        "20": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 18
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
                                0.0001689440657602903, 
                                0.00032978789581944445, 
                                -0.999999931348921, 
                                0.0, 
                                0.08575678513229013, 
                                -0.9963160518402043, 
                                -0.00031408489592298777, 
                                0.0, 
                                -0.9963160870234291, 
                                -0.08575672618221497, 
                                -0.00019660323430148452, 
                                0.0, 
                                2.1097098291503897, 
                                0.43840553783654945, 
                                0.4365359485173525, 
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
                            "value": 19
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -1.0, 
                                1.2946425113928475e-12, 
                                1.0097419586828953e-28, 
                                0.0, 
                                1.5380700742093034e-13, 
                                0.11880268573558284, 
                                0.9929178827385539, 
                                0.0, 
                                1.28547370131551e-12, 
                                0.9929178827385539, 
                                -0.11880268573558306, 
                                0.0, 
                                5.551115123125782e-17, 
                                -2.7755575615628914e-17, 
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
                                -0.0001689440656666985, 
                                -0.00032978789711063383, 
                                0.9999999313489204, 
                                0.0, 
                                -0.9790719232719549, 
                                -0.2035144097912509, 
                                -0.00023252499649761837, 
                                0.0, 
                                0.2035144725036967, 
                                -0.9790718953413287, 
                                -0.00028850351888398684, 
                                0.0, 
                                2.1097098291503897, 
                                0.43840553783654945, 
                                0.4365359485173524, 
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
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToChest_M|_:FKOffsetScapula_L|_:FKExtraScapula_L|_:FKScapula_L", 
                        "shortestPath": "_:FKScapula_L", 
                        "value": "rSocketConstraint3"
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
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.23450011014938354, 
                                0.21000000834465027, 
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
                                1.555071473121643, 
                                0.5319331884384155, 
                                0.5319331884384155
                            ]
                        }, 
                        "length": 1.555071473121643, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.7775357365608215, 
                                3.552713678800501e-15, 
                                -1.816340817917153e-15
                            ]
                        }, 
                        "radius": 0.26596659421920776, 
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
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToChest_M|_:FKOffsetNeck_M|_:FKExtraNeck_M|_:FKXNeck_M|_:FKOffsetNeckPart1_M|_:FKExtraNeckPart1_M|_:FKNeckPart1_M|_:FKXNeckPart1_M|_:FKOffsetNeckPart2_M|_:FKExtraNeckPart2_M|_:FKNeckPart2_M|_:FKXNeckPart2_M|_:FKOffsetHead_M|_:FKGlobalStaticHead_M|_:FKGlobalHead_M|_:FKExtraHead_M|_:FKHead_M", 
                        "shortestPath": "_:FKHead_M", 
                        "value": "rRigid3"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                4.440892098500626e-16, 
                                1.0, 
                                1.110223024625156e-16, 
                                0.0, 
                                -3.330669073875468e-16, 
                                0.0, 
                                1.0, 
                                0.0, 
                                1.0, 
                                -3.330669073875468e-16, 
                                4.440892098500626e-16, 
                                0.0, 
                                -1.3519366116377936e-15, 
                                15.674466033769756, 
                                -0.10534727585266479, 
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
                            "value": 23
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
                                1.0000000000000004, 
                                1.0000000000000004, 
                                0.9999999999999999
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0000000000000004, 
                                1.0000000000000004, 
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
            "id": 21
        }, 
        "22": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 18
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
                                0.9838128719329828, 
                                -0.17919886444667074, 
                                -0.0, 
                                0.0, 
                                0.17919886444667074, 
                                0.9838128719329828, 
                                0.0, 
                                0.0, 
                                0.0, 
                                -0.0, 
                                1.0, 
                                0.0, 
                                1.5550714897106417, 
                                6.661338147750939e-15, 
                                -3.4441365515717152e-15, 
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
                            "value": 21
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -0.5693814884991628, 
                                0.8220734277146281, 
                                0.0, 
                                0.0, 
                                -0.8220734277146281, 
                                -0.5693814884991628, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                -1.7763568394002513e-15, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 23
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -0.41285021268759414, 
                                0.9107989360357247, 
                                0.0, 
                                0.0, 
                                -0.9107989360357247, 
                                -0.41285021268759414, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                1.5550714897106397, 
                                6.6613381477509385e-15, 
                                -3.4441365515717164e-15, 
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
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToChest_M|_:FKOffsetNeck_M|_:FKExtraNeck_M|_:FKXNeck_M|_:FKOffsetNeckPart1_M|_:FKExtraNeckPart1_M|_:FKNeckPart1_M|_:FKXNeckPart1_M|_:FKOffsetNeckPart2_M|_:FKExtraNeckPart2_M|_:FKNeckPart2_M|_:FKXNeckPart2_M|_:FKOffsetHead_M|_:FKGlobalStaticHead_M|_:FKGlobalHead_M|_:FKExtraHead_M|_:FKHead_M", 
                        "shortestPath": "_:FKHead_M", 
                        "value": "rSocketConstraint2"
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
                                1.555071473121643, 
                                0.5319331884384155, 
                                0.5319331884384155
                            ]
                        }, 
                        "length": 1.555071473121643, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.7775357365608215, 
                                3.552713678800501e-15, 
                                -1.816340817917153e-15
                            ]
                        }, 
                        "radius": 0.26596659421920776, 
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
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToChest_M|_:FKOffsetNeck_M|_:FKExtraNeck_M|_:FKNeck_M", 
                        "shortestPath": "_:FKNeck_M", 
                        "value": "rRigid2"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                2.220446049250313e-16, 
                                0.983812871932983, 
                                0.17919886444667057, 
                                0.0, 
                                -3.3306690738754686e-16, 
                                -0.17919886444667066, 
                                0.983812871932983, 
                                0.0, 
                                1.0, 
                                -3.3306690738754686e-16, 
                                2.220446049250313e-16, 
                                0.0, 
                                1.6035764306761068e-15, 
                                14.144566685416503, 
                                -0.3840143209422106, 
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
                            "value": 15
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
                                0.9999999999999999, 
                                0.9999999999999999, 
                                0.9999999999999999
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                0.9999999999999999, 
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
            "id": 23
        }, 
        "24": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 1, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 18
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
                                0.9647868586771, 
                                0.2630329206087585, 
                                0.0, 
                                0.0, 
                                -0.2630329206087585, 
                                0.9647868586771, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                2.5642982679994653, 
                                0.25977415496934875, 
                                2.054930348185241e-15, 
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
                                3.5527136788005005e-15, 
                                -8.881784197001251e-16, 
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
                                0.9647868586770987, 
                                0.26303292060876327, 
                                0.0, 
                                0.0, 
                                -0.26303292060876327, 
                                0.9647868586770987, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                2.5642982679994617, 
                                0.2597741549693484, 
                                2.054930348185242e-15, 
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
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToChest_M|_:FKOffsetNeck_M|_:FKExtraNeck_M|_:FKNeck_M", 
                        "shortestPath": "_:FKNeck_M", 
                        "value": "rSocketConstraint1"
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
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.21000000834465027, 
                                0.699999988079071, 
                                0.5448333621025085, 
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
                                1.0925408601760864, 
                                0.5395034551620483, 
                                0.5395034551620483
                            ]
                        }, 
                        "length": 1.0925408601760864, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.5462704300880432, 
                                5.858646900946951e-13, 
                                -8.881784197001252e-15
                            ]
                        }, 
                        "radius": 0.26975172758102417, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                -0.7479313757741239, 
                                0.0, 
                                0.0, 
                                0.6637760594753521
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToChest_M|_:FKOffsetScapula_R|_:FKExtraScapula_R|_:FKScapula_R", 
                        "shortestPath": "_:FKScapula_R", 
                        "value": "rRigid8"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                -0.9999999313489201, 
                                -0.0001966441218579049, 
                                -0.00031405930075316445, 
                                0.0, 
                                -0.00031408489825466104, 
                                0.00013015436191854413, 
                                0.9999999422052577, 
                                0.0, 
                                -0.00019660323430501444, 
                                0.9999999721954653, 
                                -0.0001302161159322246, 
                                0.0, 
                                -0.43653594851735505, 
                                13.707000000000205, 
                                -0.1670000000000083, 
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
                            "value": 15
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
                                0.9999999999999999, 
                                1.0000000000000002
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0, 
                                0.9999999999999999, 
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
            "id": 25
        }, 
        "26": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 18
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
                                -0.000168944065564558, 
                                -0.0003297878981427527, 
                                -0.9999999313489201, 
                                0.0, 
                                -0.0857567851325975, 
                                0.9963160518401769, 
                                -0.000314084898254477, 
                                0.0, 
                                0.9963160870234025, 
                                0.08575672618252196, 
                                -0.00019660323430548132, 
                                0.0, 
                                2.1097098291503897, 
                                0.43840553783655034, 
                                -0.4365359485173529, 
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
                            "value": 25
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                -0.0, 
                                0.0, 
                                -0.0, 
                                -0.1188026857347475, 
                                -0.9929178827386537, 
                                0.0, 
                                0.0, 
                                0.9929178827386537, 
                                -0.1188026857347475, 
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
                                -0.0001689440656671426, 
                                -0.0003297878970754397, 
                                -0.9999999313489205, 
                                0.0, 
                                -0.9790719232720295, 
                                -0.20351440979089186, 
                                0.00023252499649073494, 
                                0.0, 
                                -0.20351447250333754, 
                                0.9790718953414034, 
                                -0.00028850351884956993, 
                                0.0, 
                                2.1097098291503897, 
                                0.43840553783655034, 
                                -0.4365359485173528, 
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
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToChest_M|_:FKOffsetScapula_R|_:FKExtraScapula_R|_:FKScapula_R", 
                        "shortestPath": "_:FKScapula_R", 
                        "value": "rSocketConstraint7"
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
            "id": 26
        }, 
        "27": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.21000000834465027, 
                                0.6183332800865173, 
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
                                2.6142518520355225, 
                                1.0804892778396606, 
                                1.0804892778396606
                            ]
                        }, 
                        "length": 2.6142518520355225, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                1.3071259260177612, 
                                -2.0261570199409107e-15, 
                                -6.394884621840902e-14
                            ]
                        }, 
                        "radius": 0.5402446389198303, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.9999980963399618, 
                                0.0, 
                                0.0, 
                                0.0019512345969743528
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToScapula_R|_:FKOffsetShoulder_R|_:FKExtraShoulder_R|_:FKShoulder_R", 
                        "shortestPath": "_:FKShoulder_R", 
                        "value": "rRigid9"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                -0.9986277024879406, 
                                4.845776557793614e-14, 
                                -0.05237090627110574, 
                                0.0, 
                                -0.05237090586174516, 
                                0.00012503251318529696, 
                                0.9986276946821027, 
                                0.0, 
                                6.548066077256833e-06, 
                                0.9999999921834353, 
                                -0.00012486093137598075, 
                                0.0, 
                                -1.5290766965528075, 
                                13.706785158269454, 
                                -0.16734312260574943, 
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
                            "value": 25
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
                                1.0000000000000007, 
                                1.0000000000000002, 
                                1.0000000000000002
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0000000000000007, 
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
            "id": 27
        }, 
        "28": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 18
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
                                0.9986440815012738, 
                                -0.052057249364012285, 
                                0.000203152972228515, 
                                0.0, 
                                0.052057249364012355, 
                                0.9986441021508385, 
                                5.291379450783442e-06, 
                                0.0, 
                                -0.00020315297220996863, 
                                5.29138016283774e-06, 
                                0.9999999793504354, 
                                0.0, 
                                1.0925408230395588, 
                                1.1885492590124613e-12, 
                                -1.5987211554602254e-14, 
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
                            "value": 27
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                0.0, 
                                -0.9999923853670951, 
                                0.003902461764974051, 
                                0.0, 
                                0.0, 
                                -0.003902461764974051, 
                                -0.9999923853670951, 
                                0.0, 
                                4.440892098500629e-16, 
                                1.387778780781446e-17, 
                                3.552713678800502e-15, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 25
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                0.9986440815012738, 
                                -0.05205724936401402, 
                                0.0002031529721783006, 
                                0.0, 
                                -0.05205764576387644, 
                                -0.9986364771931888, 
                                0.0038971703452311945, 
                                0.0, 
                                -8.276853594862964e-15, 
                                -0.0039024617653289446, 
                                -0.9999923853670936, 
                                0.0, 
                                1.092540823039559, 
                                1.1886602813149236e-12, 
                                -1.4210854715202007e-14, 
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
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToScapula_R|_:FKOffsetShoulder_R|_:FKExtraShoulder_R|_:FKShoulder_R", 
                        "shortestPath": "_:FKShoulder_R", 
                        "value": "rSocketConstraint8"
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
                                0.699999988079071, 
                                0.6754999756813049, 
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
                                2.2826035022735596, 
                                0.7480310797691345, 
                                0.7480310797691345
                            ]
                        }, 
                        "length": 2.2826035022735596, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                1.1413017511367798, 
                                8.881784197001252e-16, 
                                3.1441516057384433e-13
                            ]
                        }, 
                        "radius": 0.37401553988456726, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                -5.287791209876813e-06, 
                                0.0, 
                                0.0, 
                                0.9999999999860196
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToScapula_R|_:FKOffsetShoulder_R|_:FKExtraShoulder_R|_:FKShoulder_R|_:FKXShoulder_R|_:FKOffsetElbow_R|_:FKExtraElbow_R|_:FKElbow_R", 
                        "shortestPath": "_:FKElbow_R", 
                        "value": "rRigid10"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                -0.9982602798557887, 
                                1.272303245516276e-05, 
                                0.05896111854745212, 
                                0.0, 
                                0.05896111967558128, 
                                0.0001243231689366242, 
                                0.9982602721286425, 
                                0.0, 
                                5.370664739129393e-06, 
                                0.9999999921909369, 
                                -0.00012485704565445843, 
                                0.0, 
                                -4.139741069445498, 
                                13.706785158269453, 
                                -0.304253864053698, 
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
                            "value": 27
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
                                1.0000000000000004, 
                                1.0000000000000002, 
                                1.0000000000000002
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0000000000000004, 
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
            "id": 29
        }, 
        "30": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 18
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
                                0.9938025225442669, 
                                0.11116000262355995, 
                                -1.1755820948993775e-06, 
                                0.0, 
                                -0.11116000262355995, 
                                0.99380252254496, 
                                6.554193890791032e-08, 
                                0.0, 
                                1.1755820934706464e-06, 
                                6.554196453410138e-08, 
                                0.9999999999993069, 
                                0.0, 
                                2.6142519042768413, 
                                -4.1494585545365226e-15, 
                                -1.3145040611561853e-13, 
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
                            "value": 29
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                -0.0, 
                                0.0, 
                                -0.0, 
                                0.9999999999440785, 
                                -1.0575582419106458e-05, 
                                0.0, 
                                0.0, 
                                1.0575582419106458e-05, 
                                0.9999999999440785, 
                                0.0, 
                                8.881784197001256e-16, 
                                0.0, 
                                3.552713678800502e-15, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 27
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                0.9938025225442668, 
                                0.1111600026235609, 
                                -1.1755818198134737e-06, 
                                0.0, 
                                -0.11116000262977713, 
                                0.9938025224886919, 
                                -1.0510040480220609e-05, 
                                0.0, 
                                5.0567422894059145e-14, 
                                1.0575582419467583e-05, 
                                0.9999999999440785, 
                                0.0, 
                                2.6142519042768444, 
                                -3.802513859341162e-15, 
                                -1.2789769243681806e-13, 
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
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToScapula_R|_:FKOffsetShoulder_R|_:FKExtraShoulder_R|_:FKShoulder_R|_:FKXShoulder_R|_:FKOffsetElbow_R|_:FKExtraElbow_R|_:FKElbow_R", 
                        "shortestPath": "_:FKElbow_R", 
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
            "id": 30
        }, 
        "31": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.699999988079071, 
                                0.6591666340827942, 
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
                                2.2826035022735596, 
                                0.7480310797691345, 
                                0.7480310797691345
                            ]
                        }, 
                        "length": 2.2826035022735596, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                1.1413017511367798, 
                                8.881784197001252e-16, 
                                3.1441516057384433e-13
                            ]
                        }, 
                        "radius": 0.37401553988456726, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                -5.287791209876813e-06, 
                                0.0, 
                                0.0, 
                                0.9999999999860196
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToScapula_R|_:FKOffsetShoulder_R|_:FKExtraShoulder_R|_:FKShoulder_R|_:FKXShoulder_R|_:FKOffsetElbow_R|_:FKExtraElbow_R|_:FKElbow_R|_:FKXElbow_R|_:FKOffsetWrist_R|_:FKExtraWrist_R|_:FKWrist_R", 
                        "shortestPath": "_:FKWrist_R", 
                        "value": "rRigid11"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                -0.9999915252214038, 
                                6.464731447807999e-06, 
                                0.004116970193957593, 
                                0.0, 
                                0.0041169709059085315, 
                                0.00011427421227239165, 
                                0.9999915187100161, 
                                0.0, 
                                5.9942130926820044e-06, 
                                0.9999999934498058, 
                                -0.00011429985893518513, 
                                0.0, 
                                -6.418373455819802, 
                                13.706814199908207, 
                                -0.16966900981258637, 
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
                            "value": 29
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
                                1.0000000000000004, 
                                1.0, 
                                1.0000000000000002
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0000000000000004, 
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
            "id": 31
        }, 
        "32": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 18
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
                                0.9984945610708488, 
                                -0.05485081140326476, 
                                5.800794388532484e-07, 
                                0.0, 
                                0.0548508114063321, 
                                0.9984945610150114, 
                                -1.0559664455174414e-05, 
                                0.0, 
                                -1.1390780490063215e-15, 
                                1.0575585353126052e-05, 
                                0.9999999999440785, 
                                0.0, 
                                2.2826034776256128, 
                                2.1094237467877974e-15, 
                                6.341593916658894e-13, 
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
                            "value": 31
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -0.9999915252214038, 
                                0.004116970905908654, 
                                5.994213091947783e-06, 
                                0.0, 
                                6.4647314467862465e-06, 
                                0.00011427421220266964, 
                                0.9999999934498057, 
                                0.0, 
                                0.004116970193957716, 
                                0.999991518710016, 
                                -0.00011429985886524108, 
                                0.0, 
                                0.0, 
                                -2.7755575615628914e-17, 
                                1.776356839400251e-15, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 29
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -0.9982602798557889, 
                                0.05896111967558142, 
                                5.370664738331422e-06, 
                                0.0, 
                                1.27230324502535e-05, 
                                0.0001243231688669022, 
                                0.999999992190937, 
                                0.0, 
                                0.05896111854745226, 
                                0.9982602721286427, 
                                -0.00012485704558473643, 
                                0.0, 
                                2.28260347762561, 
                                2.2204460492503135e-15, 
                                6.288303211476888e-13, 
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
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToScapula_R|_:FKOffsetShoulder_R|_:FKExtraShoulder_R|_:FKShoulder_R|_:FKXShoulder_R|_:FKOffsetElbow_R|_:FKExtraElbow_R|_:FKElbow_R|_:FKXElbow_R|_:FKOffsetWrist_R|_:FKExtraWrist_R|_:FKWrist_R", 
                        "shortestPath": "_:FKWrist_R", 
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
            "id": 32
        }, 
        "33": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.699999988079071, 
                                0.39783331751823425, 
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
                                4.974124431610107, 
                                1.4461934566497803, 
                                1.4461934566497803
                            ]
                        }, 
                        "length": 4.974124431610107, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                -2.4870622158050537, 
                                -5.551115123125783e-16, 
                                -1.1546319456101628e-14
                            ]
                        }, 
                        "radius": 0.7230967283248901, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                4.156510876498302e-17, 
                                -0.6788097399825365, 
                                -0.7343141949498465, 
                                4.496377642068975e-17
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToRoot_M|_:FKOffsetHip_L|_:FKExtraHip_L|_:FKHip_L", 
                        "shortestPath": "_:FKHip_L", 
                        "value": "rRigid12"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                -0.03122270505701552, 
                                0.9954596111832905, 
                                -0.08991832511637822, 
                                0.0, 
                                -0.009978919864590709, 
                                -0.09026815918723274, 
                                -0.9958675015258229, 
                                0.0, 
                                -0.9994626375444251, 
                                -0.030196389515313067, 
                                0.012752027798777155, 
                                0.0, 
                                0.8196866071478003, 
                                9.619287414015018, 
                                -0.23069922884853852, 
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
                            "value": 17
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
                                1.0000000000000002, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0000000000000002, 
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
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 18
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
                                0.9982572072704029, 
                                0.05007684915825335, 
                                -0.031222705057015833, 
                                0.0, 
                                0.0497874495270382, 
                                -0.9987099834426052, 
                                -0.009978919864591457, 
                                0.0, 
                                -0.03168214011534707, 
                                0.008407029823478438, 
                                -0.9994626375444251, 
                                0.0, 
                                -0.19968944689688328, 
                                -0.08224022178153323, 
                                0.81968660714779, 
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
                            "value": 33
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -1.0, 
                                -5.66553889764798e-16, 
                                4.930380657631324e-32, 
                                0.0, 
                                4.4437469539307943e-17, 
                                -0.07843467380968105, 
                                0.996919255478782, 
                                0.0, 
                                -5.648084819729304e-16, 
                                0.996919255478782, 
                                0.07843467380968094, 
                                0.0, 
                                0.0, 
                                1.1102230246251565e-16, 
                                -2.220446049250313e-16, 
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
                                -0.998257207270403, 
                                -0.05007684915825273, 
                                0.031222705057020343, 
                                0.0, 
                                -0.03548959789923988, 
                                0.0867146216942023, 
                                -0.9956008551750957, 
                                0.0, 
                                0.0471490887891415, 
                                -0.994973810490916, 
                                -0.08834070332265131, 
                                0.0, 
                                -0.19968944689688506, 
                                -0.08224022178153345, 
                                0.8196866071477905, 
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
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToRoot_M|_:FKOffsetHip_L|_:FKExtraHip_L|_:FKHip_L", 
                        "shortestPath": "_:FKHip_L", 
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
            "id": 34
        }, 
        "35": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.21000000834465027, 
                                0.2671666145324707, 
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
                                3.830179452896118, 
                                0.9973747730255127, 
                                0.9973747730255127
                            ]
                        }, 
                        "length": 3.830179452896118, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                -1.915089726448059, 
                                7.896461262646426e-15, 
                                -2.886579864025407e-15
                            ]
                        }, 
                        "radius": 0.49868738651275635, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.0, 
                                1.0, 
                                0.0, 
                                7.273661547324616e-16
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToRoot_M|_:FKOffsetHip_L|_:FKExtraHip_L|_:FKHip_L|_:FKXHip_L|_:FKOffsetKnee_L|_:FKExtraKnee_L|_:FKKnee_L", 
                        "shortestPath": "_:FKKnee_L", 
                        "value": "rRigid13"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                -0.029165783643122944, 
                                0.9967971273953009, 
                                0.07446370848244861, 
                                0.0, 
                                -0.014959719824376775, 
                                0.07405177159741694, 
                                -0.9971421874066206, 
                                0.0, 
                                -0.9994626375444251, 
                                -0.030196389515313178, 
                                0.012752027798777044, 
                                0.0, 
                                0.9749922335609716, 
                                4.6677472383161795, 
                                0.21656572730177473, 
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
                            "value": 33
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
                                1.0000000000000002, 
                                1.0, 
                                1.0
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0000000000000002, 
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
            "id": 35
        }, 
        "36": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 18
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
                                0.986486263577297, 
                                -0.16384398607609568, 
                                -0.0, 
                                0.0, 
                                0.16384398607609568, 
                                0.986486263577297, 
                                0.0, 
                                0.0, 
                                0.0, 
                                -0.0, 
                                1.0, 
                                0.0, 
                                -4.974124635567105, 
                                -3.6637359812630166e-15, 
                                -2.5091040356528538e-14, 
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
                            "value": 35
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -1.0, 
                                0.0, 
                                -1.4547323094649232e-15, 
                                0.0, 
                                0.0, 
                                1.0, 
                                0.0, 
                                0.0, 
                                1.4547323094649232e-15, 
                                0.0, 
                                -1.0, 
                                0.0, 
                                8.881784197001254e-16, 
                                1.3877787807814457e-17, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 33
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -0.9864862635772962, 
                                0.16384398607609985, 
                                1.9721522630525295e-31, 
                                0.0, 
                                0.16384398607609985, 
                                0.9864862635772963, 
                                2.0994657542867678e-14, 
                                0.0, 
                                3.439848378126096e-15, 
                                2.0710941274548437e-14, 
                                -1.0, 
                                0.0, 
                                -4.974124635567107, 
                                -3.4416913763379853e-15, 
                                -2.4202861936828413e-14, 
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
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToRoot_M|_:FKOffsetHip_L|_:FKExtraHip_L|_:FKHip_L|_:FKXHip_L|_:FKOffsetKnee_L|_:FKExtraKnee_L|_:FKKnee_L", 
                        "shortestPath": "_:FKKnee_L", 
                        "value": "rSocketConstraint12"
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
                                0.6755000352859497, 
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
                                1.498598337173462, 
                                0.6150477528572083, 
                                0.6150477528572083
                            ]
                        }, 
                        "length": 1.498598337173462, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                -0.33305853605270386, 
                                -0.6712087988853455, 
                                2.220446049250313e-16
                            ]
                        }, 
                        "radius": 0.3075238764286041, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                0.008038264140787362, 
                                -0.012962102252806567, 
                                -0.8497521311737671, 
                                0.5269617498267133
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToRoot_M|_:FKOffsetHip_L|_:FKExtraHip_L|_:FKHip_L|_:FKXHip_L|_:FKOffsetKnee_L|_:FKExtraKnee_L|_:FKKnee_L|_:FKXKnee_L|_:FKOffsetAnkle_L|_:FKExtraAnkle_L|_:FKAnkle_L", 
                        "shortestPath": "_:FKAnkle_L", 
                        "value": "rRigid14"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                1.1102230246251565e-15, 
                                1.0, 
                                5.551115123125784e-17, 
                                0.0, 
                                0.012108272557155245, 
                                0.0, 
                                -0.9999266921808226, 
                                0.0, 
                                -0.9999266921808228, 
                                1.1102230246251567e-15, 
                                -0.012108272557155297, 
                                0.0, 
                                1.08670241991475, 
                                0.8498353241101171, 
                                -0.06864364176413394, 
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
                            "value": 35
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
                                1.0000000000000002, 
                                1.0, 
                                0.9999999999999999
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                1.0000000000000002, 
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
            "id": 37
        }, 
        "38": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 18
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
                                0.9967971273953008, 
                                0.07405177159741688, 
                                -0.030196389515314254, 
                                0.0, 
                                -0.07481139696806574, 
                                0.9968879527224399, 
                                -0.024852859001510543, 
                                0.0, 
                                0.028262018685208307, 
                                0.027032292543298666, 
                                0.9992349640898733, 
                                0.0, 
                                -3.8301794911694094, 
                                1.569577801063815e-14, 
                                -5.329070518200751e-15, 
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
                            "value": 37
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -0.4444934010583428, 
                                -0.8957821255280702, 
                                0.0, 
                                0.0, 
                                0.8953653543211584, 
                                -0.4442865962495126, 
                                0.03050086350202652, 
                                0.0, 
                                -0.027322128338286854, 
                                0.01355743255323204, 
                                0.9995347404295815, 
                                0.0, 
                                -1.1102230246251568e-16, 
                                2.7755575615628914e-17, 
                                -2.2204460492503128e-16, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 35
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                -0.37605503313134503, 
                                -0.925909933014765, 
                                0.03568484273716766, 
                                0.0, 
                                0.9265973300504285, 
                                -0.3757760563777568, 
                                0.014482520381408702, 
                                0.0, 
                                -1.793704074160019e-15, 
                                0.03851170468538501, 
                                0.999258149129756, 
                                0.0, 
                                -3.8301794911694103, 
                                1.572353358625378e-14, 
                                -5.551115123125783e-15, 
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
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToRoot_M|_:FKOffsetHip_L|_:FKExtraHip_L|_:FKHip_L|_:FKXHip_L|_:FKOffsetKnee_L|_:FKExtraKnee_L|_:FKKnee_L|_:FKXKnee_L|_:FKOffsetAnkle_L|_:FKExtraAnkle_L|_:FKAnkle_L", 
                        "shortestPath": "_:FKAnkle_L", 
                        "value": "rSocketConstraint13"
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
                                0.46316662430763245, 
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
                                4.974124431610107, 
                                1.4461934566497803, 
                                1.4461934566497803
                            ]
                        }, 
                        "length": 4.974124431610107, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                2.4870622158050537, 
                                9.992007221626409e-16, 
                                1.3100631690576847e-14
                            ]
                        }, 
                        "radius": 0.7230967283248901, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                -0.6788097399825366, 
                                0.0, 
                                0.0, 
                                0.7343141949498465
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToRoot_M|_:FKOffsetHip_R|_:FKExtraHip_R|_:FKHip_R", 
                        "shortestPath": "_:FKHip_R", 
                        "value": "rRigid16"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                -0.031222705057015077, 
                                -0.9954596111832904, 
                                0.08991832511637837, 
                                0.0, 
                                -0.009978919864591984, 
                                0.09026815918723274, 
                                0.9958675015258227, 
                                0.0, 
                                -0.9994626375444249, 
                                0.030196389515312783, 
                                -0.012752027798778487, 
                                0.0, 
                                -0.8196866071477907, 
                                9.619287414015057, 
                                -0.23069922884853314, 
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
                            "value": 17
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
            "id": 39
        }, 
        "40": {
            "components": {
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 18
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
                                -0.998257207270403, 
                                -0.05007684915825318, 
                                -0.03122270505701527, 
                                0.0, 
                                -0.049787449527038036, 
                                0.9987099834426052, 
                                -0.00997891986459178, 
                                0.0, 
                                0.03168214011534652, 
                                -0.008407029823478795, 
                                -0.9994626375444251, 
                                0.0, 
                                -0.19968944689688684, 
                                -0.08224022178153434, 
                                -0.8196866071477904, 
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
                            "value": 39
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                -0.0, 
                                0.0, 
                                -0.0, 
                                0.07843467380968161, 
                                -0.996919255478782, 
                                0.0, 
                                0.0, 
                                0.996919255478782, 
                                0.07843467380968161, 
                                0.0, 
                                0.0, 
                                2.220446049250313e-16, 
                                -2.2204460492503128e-16, 
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
                                -0.9982572072704028, 
                                -0.050076849158252404, 
                                -0.03122270505702033, 
                                0.0, 
                                -0.03548959789923989, 
                                0.08671462169420352, 
                                0.9956008551750954, 
                                0.0, 
                                -0.04714908878914114, 
                                0.9949738104909158, 
                                -0.08834070332265243, 
                                0.0, 
                                -0.19968944689688506, 
                                -0.08224022178153345, 
                                -0.8196866071477905, 
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
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToRoot_M|_:FKOffsetHip_R|_:FKExtraHip_R|_:FKHip_R", 
                        "shortestPath": "_:FKHip_R", 
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
            "id": 40
        }, 
        "41": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.5530000329017639, 
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
                                3.830179452896118, 
                                0.9973747730255127, 
                                0.9973747730255127
                            ]
                        }, 
                        "length": 3.830179452896118, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                1.915089726448059, 
                                2.609024107869118e-15, 
                                3.774758283725532e-15
                            ]
                        }, 
                        "radius": 0.49868738651275635, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                -1.0, 
                                0.0, 
                                0.0, 
                                8.94301653695862e-15
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToRoot_M|_:FKOffsetHip_R|_:FKExtraHip_R|_:FKHip_R|_:FKXHip_R|_:FKOffsetKnee_R|_:FKExtraKnee_R|_:FKKnee_R", 
                        "shortestPath": "_:FKKnee_R", 
                        "value": "rRigid17"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                -0.02916578364312228, 
                                -0.9967971273953007, 
                                -0.07446370848244932, 
                                0.0, 
                                -0.014959719824378548, 
                                -0.0740517715974176, 
                                0.9971421874066204, 
                                0.0, 
                                -0.9994626375444249, 
                                0.030196389515313005, 
                                -0.012752027798778709, 
                                0.0, 
                                -0.9749922335609505, 
                                4.667747238316194, 
                                0.21656572730177703, 
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
                            "value": 39
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
                                0.9999999999999996, 
                                0.9999999999999997, 
                                0.9999999999999996
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                0.9999999999999996, 
                                0.9999999999999997, 
                                0.9999999999999996
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
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 18
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
                                0.9864862635772967, 
                                -0.16384398607609663, 
                                -0.0, 
                                0.0, 
                                0.16384398607609663, 
                                0.9864862635772967, 
                                0.0, 
                                0.0, 
                                0.0, 
                                -0.0, 
                                1.0, 
                                0.0, 
                                4.974124635567098, 
                                3.6637359812630166e-15, 
                                2.4646951146678475e-14, 
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
                            "value": 41
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                1.0, 
                                0.0, 
                                -0.0, 
                                0.0, 
                                -0.0, 
                                -1.0, 
                                -1.788603307391724e-14, 
                                0.0, 
                                0.0, 
                                1.788603307391724e-14, 
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
                            "value": 39
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                0.9864862635772971, 
                                -0.16384398607609513, 
                                0.0, 
                                0.0, 
                                -0.16384398607609513, 
                                -0.9864862635772971, 
                                -1.7886033073917243e-14, 
                                0.0, 
                                2.930518953919473e-15, 
                                1.7644325937308575e-14, 
                                -1.0, 
                                0.0, 
                                4.974124635567098, 
                                3.4416913763379853e-15, 
                                2.442490654175344e-14, 
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
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToRoot_M|_:FKOffsetHip_R|_:FKExtraHip_R|_:FKHip_R|_:FKXHip_R|_:FKOffsetKnee_R|_:FKExtraKnee_R|_:FKKnee_R", 
                        "shortestPath": "_:FKKnee_R", 
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
            "id": 42
        }, 
        "43": {
            "components": {
                "ColorComponent": {
                    "members": {
                        "value": {
                            "type": "Color4", 
                            "values": [
                                0.699999988079071, 
                                0.43050000071525574, 
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
                                1.498598337173462, 
                                0.6150477528572083, 
                                0.6150477528572083
                            ]
                        }, 
                        "length": 1.498598337173462, 
                        "offset": {
                            "type": "Vector3", 
                            "values": [
                                0.33305853605270386, 
                                0.6712087988853455, 
                                -1.1102230246251565e-15
                            ]
                        }, 
                        "radius": 0.3075238764286041, 
                        "rotation": {
                            "type": "Quaternion", 
                            "values": [
                                -0.012962102252807068, 
                                -0.008038264140787713, 
                                0.5269617498267152, 
                                0.8497521311737659
                            ]
                        }, 
                        "type": "Capsule"
                    }, 
                    "type": "GeometryDescriptionComponent"
                }, 
                "NameComponent": {
                    "members": {
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToRoot_M|_:FKOffsetHip_R|_:FKExtraHip_R|_:FKHip_R|_:FKXHip_R|_:FKOffsetKnee_R|_:FKExtraKnee_R|_:FKKnee_R|_:FKXKnee_R|_:FKOffsetAnkle_R|_:FKExtraAnkle_R|_:FKAnkle_R", 
                        "shortestPath": "_:FKAnkle_R", 
                        "value": "rRigid18"
                    }, 
                    "type": "NameComponent"
                }, 
                "RestComponent": {
                    "members": {
                        "matrix": {
                            "type": "Matrix44", 
                            "values": [
                                2.220446049250313e-15, 
                                -1.0, 
                                0.0, 
                                0.0, 
                                0.012108272557153632, 
                                0.0, 
                                0.9999266921808228, 
                                0.0, 
                                -0.9999266921808228, 
                                -2.3869795029440866e-15, 
                                0.012108272557153521, 
                                0.0, 
                                -1.0867024199147295, 
                                0.8498353241101212, 
                                -0.06864364176411394, 
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
                            "value": 41
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
                                0.9999999999999997, 
                                0.9999999999999996, 
                                0.9999999999999994
                            ]
                        }, 
                        "value": {
                            "type": "Vector3", 
                            "values": [
                                0.9999999999999997, 
                                0.9999999999999996, 
                                0.9999999999999994
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
                "ConstraintUIComponent": {
                    "members": {
                        "childIndex": 2, 
                        "multiplierEntity": {
                            "type": "Entity", 
                            "value": 18
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
                                0.9967971273953007, 
                                0.07405177159741776, 
                                -0.030196389515315034, 
                                0.0, 
                                -0.07481139696806662, 
                                0.9968879527224398, 
                                -0.02485285900151026, 
                                0.0, 
                                0.028262018685209087, 
                                0.027032292543298465, 
                                0.9992349640898733, 
                                0.0, 
                                3.8301794911694174, 
                                5.093148125467906e-15, 
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
                        "strength": 0.5
                    }, 
                    "type": "DriveUIComponent"
                }, 
                "JointComponent": {
                    "members": {
                        "child": {
                            "type": "Entity", 
                            "value": 43
                        }, 
                        "childFrame": {
                            "type": "Matrix44", 
                            "values": [
                                0.4444934010583388, 
                                0.8957821255280721, 
                                1.734723475976807e-18, 
                                0.0, 
                                -0.8953653543211603, 
                                0.4442865962495085, 
                                -0.030500863502027856, 
                                0.0, 
                                -0.027322128338288114, 
                                0.013557432553232513, 
                                0.9995347404295813, 
                                0.0, 
                                3.3306690738754686e-16, 
                                0.0, 
                                0.0, 
                                1.0
                            ]
                        }, 
                        "disableCollision": true, 
                        "parent": {
                            "type": "Entity", 
                            "value": 41
                        }, 
                        "parentFrame": {
                            "type": "Matrix44", 
                            "values": [
                                0.3760550331313399, 
                                0.9259099330147672, 
                                -0.035684842737167946, 
                                0.0, 
                                -0.9265973300504308, 
                                0.3757760563777518, 
                                -0.014482520381409078, 
                                0.0, 
                                -2.2482016248659424e-15, 
                                0.038511704685385416, 
                                0.999258149129756, 
                                0.0, 
                                3.830179491169416, 
                                5.1070259132757185e-15, 
                                7.32747196252603e-15, 
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
                        "path": "|_:Group|_:Main|_:MotionSystem|_:FKSystem|_:FKParentConstraintToRoot_M|_:FKOffsetHip_R|_:FKExtraHip_R|_:FKHip_R|_:FKXHip_R|_:FKOffsetKnee_R|_:FKExtraKnee_R|_:FKKnee_R|_:FKXKnee_R|_:FKOffsetAnkle_R|_:FKExtraAnkle_R|_:FKAnkle_R", 
                        "shortestPath": "_:FKAnkle_R", 
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
            "id": 44
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
                        "collide": true, 
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
                        "useGround": true, 
                        "velocityIterations": 1
                    }, 
                    "type": "SolverComponent"
                }
            }, 
            "id": 1048576
        }
    }, 
    "info": {
        "entitiesCount": 45, 
        "mayaVersion": "20200200", 
        "ragdollVersion": "2021.03.29", 
        "registryAlive": 45, 
        "registrySize": 45, 
        "serialisationTimeMs": 1.8978000000000002, 
        "timestamp": 1618048251
    }, 
    "schema": "ragdoll-1.0", 
    "ui": {
        "description": "", 
        "filename": "C:/Users/marcus/Documents/maya/projects/default/scenes/demo/mycharacter.rag", 
        "thumbnail": "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"
    }
}
```