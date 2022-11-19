import os
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--fname")
opts = parser.parse_args()

dirname = os.path.dirname(__file__)
assets = os.path.join(dirname, "ragdoll", "resources", "assets")

for asset in [opts.fname] if opts.fname else os.listdir(assets):
    fname = os.path.join(assets, asset)

    with open(fname) as f:
        content = json.load(f)

    for entity, data in content["entities"].items():
        components = data["components"]

        if "GroupUIComponent" in components:
            ui = components["GroupUIComponent"]["members"]
            ui["useLinearAngularStiffness"] = True

            ang_stiffness = ui["stiffness"]
            ang_damping = ui["dampingRatio"]
            lin_stiffness = ui["driveRelativeLinearStiffness"]
            lin_damping = ui["driveRelativeLinearDampingRatio"]

            ui["angularStiffness"] = ang_stiffness
            ui["angularDampingRatio"] = ang_damping
            ui["linearStiffness"] = lin_stiffness
            ui["linearDampingRatio"] = lin_damping

        if "MarkerUIComponent" in components:
            ui = components["MarkerUIComponent"]["members"]
            ui["useLinearAngularStiffness"] = True

            ang_stiffness = ui["driveStiffness"]
            ang_damping = ui["driveDampingRatio"]
            lin_stiffness = ui["driveRelativeLinearStiffness"]
            lin_damping = ui["driveRelativeLinearDampingRatio"]

            ui["angularStiffness"] = ang_stiffness
            ui["angularDampingRatio"] = ang_damping
            ui["linearStiffness"] = lin_stiffness
            ui["linearDampingRatio"] = lin_damping

        if "PinJointComponent" in components:
            con = components["DriveComponent"]["members"]
            con["useScale"] = True

        if "DistanceJointComponent" in components:
            con = components["DistanceJointComponent"]["members"]
            con["useScale"] = True
            con["useScaleForDistance"] = True

    with open(fname, "w") as f:
        json.dump(content, f, sort_keys=True, indent=4)

    print("Upgraded %s" % fname)
