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

            if ui["linearMotion"] in ("Inherit", "Locked"):
                lin_stiffness = -1
                lin_damping = 1

            ui["angularStiffness"] = ang_stiffness
            ui["angularDampingRatio"] = ang_damping
            ui["linearStiffness"] = lin_stiffness
            ui["linearDampingRatio"] = lin_damping
            ui["linearMotion"] = "Locked"

        if "MarkerUIComponent" in components:
            ui = components["MarkerUIComponent"]["members"]
            ui["useLinearAngularStiffness"] = True

            ang_stiffness = ui["driveStiffness"]
            ang_damping = ui["driveDampingRatio"]
            lin_stiffness = ui["driveRelativeLinearStiffness"]
            lin_damping = ui["driveRelativeLinearDampingRatio"]

            if ui["linearMotion"] == "Inherit":
                group = components["GroupComponent"]["members"]
                group_entity = str(group["entity"]["value"])
                if group_entity != "0":
                    group_data = content["entities"][group_entity]
                    group_ui = group_data["components"]["GroupUIComponent"]
                    ui["linearMotion"] = group_ui["members"]["linearMotion"]

            if ui["linearMotion"] == "Locked":
                lin_stiffness = -1
                lin_damping = 1

            ui["angularStiffness"] = ang_stiffness
            ui["angularDampingRatio"] = ang_damping
            ui["linearStiffness"] = lin_stiffness
            ui["linearDampingRatio"] = lin_damping
            ui["linearMotion"] = "Locked"

    with open(fname, "w") as f:
        json.dump(content, f, sort_keys=True, indent=4)

    print("Upgraded %s" % fname)
