<img width=49% src=https://user-images.githubusercontent.com/8775944/104851801-0c328e80-58ef-11eb-862f-8c57b9e409ed.gif> <img width=49% src=https://user-images.githubusercontent.com/8775944/105234661-7f443b00-5b63-11eb-93cf-692ccfb902aa.gif>

In this tutorial you'll learn how to **setup a tail** with physics and **how to steer** the look and feel of the simulation using normal keyframing techniques. We'll use one of the excellent rigs by [Truong CG Artist](https://gumroad.com/truongcgartist?sort=page_layout#krsIT).

**Optional example files**

- [falloff_example.zip](https://github.com/mottosso/upload/files/5848441/falloff_example.zip)

<br>

## Walkcycle

Let's start with a walkcycle, and move towards interacting with the environment.

### Apply Simulation

Select the hip followed by each tail control along the tail in order, and click **Create Dynamic Control**.

![01_Setup](https://user-images.githubusercontent.com/8775944/104849638-c4a60580-58e2-11eb-926a-36fa00099dff.gif)

### Reduce Gravity

This particular rig is very small, about 1.6 cm tall, so we need to reduce the default **Gravity** to reflect this.

![01_B_Gravity](https://user-images.githubusercontent.com/8775944/104851250-dcce5280-58eb-11eb-9fc8-a782e7d9cd91.gif)

### Global Strength

The first selected Dynamic Control contains a **Guide Multiplier** to influence the strength on all of the tail controls at the same time.

![02_Multiplier](https://user-images.githubusercontent.com/8775944/104851332-4c444200-58ec-11eb-9631-2c844eb75647.gif)

### Local Strength

You can also adjust the strength values individually for each joints, to taper their **stiffness** along the length of the tail.

![03_Falloff](https://user-images.githubusercontent.com/8775944/104849556-3467c080-58e2-11eb-899e-e640a8e3b284.gif)

### Strength Falloff

Let's taper the strength along the length of the tail.

![tweaking_values](https://user-images.githubusercontent.com/8775944/104852123-c8d91f80-58f0-11eb-97e8-afc2fa83ca1f.gif)

### Result

Let's see how it looks.

![wolf_animated](https://user-images.githubusercontent.com/8775944/104851801-0c328e80-58ef-11eb-862f-8c57b9e409ed.gif)

<br>

## Sitting Down

Now let's see how to steer our simulation with regular keyframes.

### Switch to Animation

The simulation will try to follow your keyframe animation. Just switch off the `Simulated` attribute on the root control while you're animating, then switch it back on to see how it looks.

![animate](https://user-images.githubusercontent.com/8775944/104857605-9986da80-5911-11eb-9f2b-26a559f7e777.gif)

### Animation vs Simulation

You can see the animation input on the left and the resulting simulation on the right. With just 3 keyframed poses we end up with this result. Note that I had to overcompensate my animation poses to fight gravity when the tail swings around.

![anim_input](https://user-images.githubusercontent.com/8775944/105234661-7f443b00-5b63-11eb-93cf-692ccfb902aa.gif)

<br>

## Advanced Control

Gain even more fine-grained control with these advanced topics.

### Flex and Relax Muscles

By keyframing the root strength multiplier you can flex or relax the muscles in the tail. The higher the value the stiffer it gets and the lower the value the more relaxed it becomes, allowing gravity to drop it to the ground.

![key_str_mult_3](https://user-images.githubusercontent.com/8775944/105247183-452b6700-5b6c-11eb-8a1e-9f19fce9eb6f.gif)

### Damping

Damping controls how fleshy and sluggish your simulation behaves.

![04_Damping](https://user-images.githubusercontent.com/8775944/104849540-20bc5a00-58e2-11eb-899e-3dfa148b9b60.gif)

Low or zero damping preserves more energy in the system, making a simulation more elastic or rubbery. Creatures and humans tend to look best with moderate to high damping values.

<!-- 
### World Space Forces

Using worldspace forces, you can apply an attraction force to the simulated tail forcing it to match your animated poses better in world space. With lower values you can just slightly guide the tail to achieve the pose you are looking for while with higher values you can completely overwrite the sim to follow your animation 100%.
 -->
