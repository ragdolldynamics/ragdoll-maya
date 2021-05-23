---
hide:
  - navigation # Hide navigation
  - toc        # Hide table of contents
---

<script src="https://js.stripe.com/v3/"></script>
<link rel="stylesheet" href="/pricing.css">
<script type="text/javascript">

  function toggle_billing(value) {
      let hashParams = new URLSearchParams(location.hash.substring(1));

      if (value === "lifetime") { hashParams.set('billing', 'lifetime'); }
      else                      { hashParams.set('billing', 'subscription'); }

      location.hash = hashParams.toString();
  }

  function toggle_licencing(value) {
      let hashParams = new URLSearchParams(location.hash.substring(1));

      if (value === "node")     { hashParams.set('licence', 'node'); }
      else                      { hashParams.set('licence', 'float'); }

      location.hash = hashParams.toString();
  }

  function toggle_currency(value) {
      let hashParams = new URLSearchParams(location.hash.substring(1));

      if (value === "gbp")      { hashParams.set('currency', 'gbp'); }
      else                      { hashParams.set('currency', 'usd'); }

      location.hash = hashParams.toString();
  }

  function update_options() {
      let urlParameters = new URLSearchParams(location.hash.substring(1));
      let billing = urlParameters.get('billing') || 'lifetime';
      let licence = urlParameters.get('licence') || 'node';

      let node = document.getElementById('node-locked');
      let floating = document.getElementById('floating');
      let nodeSubscription = document.getElementById('node-locked-subscription');
      let floatSubscription = document.getElementById('floating-subscription');

      let lifetimeButton = document.getElementById('billing-lifetime');
      let subscriptionButton = document.getElementById('billing-subscription');
      let nodeButton = document.getElementById('licence-node');
      let floatButton = document.getElementById('licence-float');

      if (billing === 'lifetime') {
          lifetimeButton.checked = true;
          subscriptionButton.checked = false;
        
        if (licence === 'node') {
              nodeButton.checked = true;
              floatButton.checked = false;
            
              node.style.display = 'flex';
              floating.style.display = 'none';
              nodeSubscription.style.display = 'none';
              floatSubscription.style.display = 'none';
          }
          else {
              nodeButton.checked = false;
              floatButton.checked = true;
            
              node.style.display = 'none';
              floating.style.display = 'flex';
              nodeSubscription.style.display = 'none';
              floatSubscription.style.display = 'none';
          }

      // Subscription

      } else {
          subscriptionButton.checked = true;
          lifetimeButton.checked = false;
         
        if (licence === 'node') {
              nodeButton.checked = true;
              floatButton.checked = false;
             
              node.style.display = 'none';
              floating.style.display = 'none';
              nodeSubscription.style.display = 'flex';
              floatSubscription.style.display = 'none';
          } else {
              nodeButton.checked = false;
              floatButton.checked = true;
            
              node.style.display = 'none';
              floating.style.display = 'none';
              nodeSubscription.style.display = 'none';
              floatSubscription.style.display = 'flex';
          }
      }
  }

  // Buttons cause the hash to change, which in
  // turn causes options to change.
  window.addEventListener('hashchange', () => {
      update_options();
  });

  window.addEventListener('load', function () {
    if (location.hash === '') {
        location.hash = 'billing=lifetime&licence=node'
      }
    
    update_options();
  })


  var stripe = Stripe(
      "pk_test_51I6CfDKRRjH6QdIZesJt6DDl2Y4jGW5Ss2luwUgqRv8gAyeBa4ID1E5c4YkG6GPt6zOVuuLxqMcNNJtOmz2VvKJL000vDq3Cxw"
  );
  var checkoutStandard = document.getElementById("get-standard");
  var checkoutFull = document.getElementById("get-complete");
  var checkoutBatch = document.getElementById("get-batch");

  function onClick(e) {
      // Create a new Checkout Session using the server-side endpoint you
      // created in step 3.
      fetch(this.id, {
        method: "POST",
      })

      .then(function(response) {
        return response.json();
      })

      .then(function(session) {
        return stripe.redirectToCheckout({ sessionId: session.id });
      })

      .then(function(result) {
        if (result.error) {
          alert(result.error.message);
        }
      })

      .catch(function(error) {
        console.error("Error:", error);
      });
    }

  checkoutStandard.addEventListener("click", onClick);
  checkoutFull.addEventListener("click", onClick);
  checkoutBatch.addEventListener("click", onClick);

</script>



<section>
<div class="backdrop backdrop2"></div>


<div class="vboxlayout align-center">
<h2>PRICING</h2>
<p style="margin-top: 0; color: #ccc;">Per user</p>

<div class="hboxlayout">

<div class="option">
  <div class="switch-field">
      <input type="radio" id="billing-lifetime" name="switch-one" onclick="toggle_billing('lifetime')" checked="">
      <label for="billing-lifetime">Lifetime</label>
      <input type="radio" id="billing-subscription" name="switch-one" onclick="toggle_billing('subscription')">
      <label for="billing-subscription">Subscription</label>
  </div>
</div>


<div class="option">
  <div class="switch-field">
      <input type="radio" id="licence-node" name="switch-two" onclick="toggle_licencing('node')" checked="">
      <label for="licence-node">Node Locked</label>
      <input type="radio" id="licence-float" name="switch-two" onclick="toggle_licencing('float')">
      <label for="licence-float">Floating</label>
  </div>
</div>


<div class="option">
  <div class="switch-field">
      <input type="radio" id="currency-one" name="switch-three" onclick="toggle_currency('gbp')" checked="">
      <label for="currency-one">GBP</label>
      <input type="radio" id="currency-two" name="switch-three" onclick="toggle_currency('usd')">
      <label for="currency-two">USD</label>
  </div>
</div>
</div>




<div id="node-locked" class="hboxlayout">


<!--

Apprentice

 -->


<div class="vboxlayout" markdown=1>

<div class="vboxlayout product lightblue">
<h2 class="product">Apprentice</h2>
<p class="type">Non-commercial</p>
<h2 class="price">Free</h2>
<div class="spacer"></div>
<a href="https://learn.ragdolldynamics.com/download" class="button blue text-white">Download</a>
</div>

<table>
  <tr><td>Non-commercial</td></tr>
  <tr><td>All features</td></tr>
  <tr><td>30-days trial</td></tr>
</table>

</div>

<!-- 


Node-locked

   ______________
  |              |
  |              |
  |              |
  |              |
  |______________|
      ___|_|__
   __/________\__
  |              |
  |        ----o |
  |______________|



-->



<!--

Standard

 -->


<div class="vboxlayout" markdown=1>
<div class="vboxlayout product lightgreen">

<h2 class="product">Standard</h2>
<p class="type">Individuals</p>
<h2 class="price">£499</h2>
<div class="spacer"></div>
<button id="get-standard">Add to cart</button>

</div>

<table>
  <tr><td>High-performance solver</td></tr>
  <tr><td>Artist tools</td></tr>
  <tr><td>Concurrent activations</td></tr>
  <tr><td>Community support</td></tr>
</table>

</div>  


<!--

Complete

 -->

<div class="vboxlayout" markdown=1>
<div class="vboxlayout product salmon">

<h2 class="product">Complete</h2>
<p class="type">Studios</p>
<h2 class="price earlybird">£499</h2>
<h2 class="price" style="text-decoration: line-through;">£1299</h2>
<div class="spacer"></div>
<button id="get-complete">Add to cart</button>

</div>

<table>
  <tr><td>Multi-threading</td></tr>
  <tr><td>JSON Export</td></tr>
  <tr><td>Python API</td></tr>
  <tr><td>Community support</td></tr>
</table>

</div>



<!--

Batch

 -->


<div class="vboxlayout" markdown=1>
<div class="vboxlayout product rust">

<h2 class="product">Batch</h2>
<p class="type">Non-interactive</p>
<h2 class="price">£199</h2>
<div class="spacer"></div>
<button id="get-batch">Add to cart</button>

</div>

<table>
  <tr><td>Headless</td></tr>
  <tr><td>Render farms</td></tr>
  <tr><td>Automation</td></tr>
</table>

</div>
</div> <!--  End of Node-locked  -->


<div id="floating" style="display: none" class="hboxlayout">




<!-- 


Floating

 _____          _____          _____          _____  
/     \        /     \        /     \        /     \ 
       \______/       \______/       \______/       \

-->




<!--

Apprentice

 -->


<div class="vboxlayout" markdown=1>

<div class="vboxlayout product lightblue">
<h2 class="product">Apprentice</h2>
<p class="type">Non-commercial</p>
<h2 class="price">Free</h2>
<div class="spacer"></div>
<a href="https://learn.ragdolldynamics.com/download" class="button blue text-white">Download</a>
</div>

<table>
  <tr><td>Non-commercial</td></tr>
  <tr><td>All features</td></tr>
  <tr><td>30-days trial</td></tr>
</table>

</div>


<!--

Standard

 -->


<div class="vboxlayout" markdown=1>
<div class="vboxlayout product gold">

<h2 class="product">Standard</h2>
<p class="type">Individuals</p>
<h2 class="price">£750</h2>
<div class="spacer"></div>
<button id="get-standard-floating">Add to cart</button>

</div>

<table>
  <tr><td>High-performance solver</td></tr>
  <tr><td>Artist tools</td></tr>
  <tr><td>Concurrent activations</td></tr>
  <tr><td>Community support</td></tr>
</table>

</div>  


<!--

Complete

 -->


<div class="vboxlayout" markdown=1>
<div class="vboxlayout product rust">

<h2 class="product">Complete</h2>
<p class="type">Studios</p>
<h2 class="price earlybird">£750</h2>
<h2 class="price" style="text-decoration: line-through;">£1950</h2>
<div class="spacer"></div>
<button id="get-complete-floating">Add to cart</button>

</div>

<table>
  <tr><td>Multi-threading</td></tr>
  <tr><td>JSON Export</td></tr>
  <tr><td>Python API</td></tr>
  <tr><td>Community support</td></tr>
</table>

</div>




<!--

Batch

 -->


<div class="vboxlayout" markdown=1>
<div class="vboxlayout product salmon">

<h2 class="product">Batch</h2>
<p class="type">Non-interactive</p>
<h2 class="price">£299</h2>

<div class="spacer"></div>

<button id="get-batch-floating">Add to cart</button>

</div>

<table>
  <tr><td>Headless</td></tr>
  <tr><td>Render farms</td></tr>
  <tr><td>Automation</td></tr>
</table>

</div>


</div> <!--  End of Floating  -->


<div id="node-locked-subscription" style="display: none" class="hboxlayout">


<!-- 


Node-locked

   ______________
  |              |
  |              |
  |              |
  |              |
  |______________|
      ___|_|__
   __/________\__
  |              |
  |        ----o |
  |______________|



-->


<!--

Apprentice

 -->


<div class="vboxlayout" markdown=1>

<div class="vboxlayout product lightblue">
<h2 class="product">Apprentice</h2>
<p class="type">Non-commercial</p>
<h2 class="price">Free</h2>
<div class="spacer"></div>
<a href="https://learn.ragdolldynamics.com/download" class="button blue text-white">Download</a>
</div>

<table>
  <tr><td>Non-commercial</td></tr>
  <tr><td>All features</td></tr>
  <tr><td>30-days trial</td></tr>
</table>

</div>



<!--

Standard

 -->


<div class="vboxlayout" markdown=1>
<div class="vboxlayout product gold">

<h2 class="product">Standard</h2>
<p class="type">Individuals</p>
<h2 class="price">£55</h2>
<div class="spacer"></div>
<button id="get-standard">Add to cart</button>

</div>

<table>
  <tr><td>High-performance solver</td></tr>
  <tr><td>Artist tools</td></tr>
  <tr><td>Concurrent activations</td></tr>
  <tr><td>Community support</td></tr>
</table>

</div>


<!--

Complete

 -->


<div class="vboxlayout" markdown=1>
<div class="vboxlayout product rust">

<h2 class="product">Complete</h2>
<p class="type">Studios</p>
<h2 class="price earlybird">£55</h2>
<h2 class="price" style="text-decoration: line-through;">£145</h2>
<div class="spacer"></div>
<button id="get-complete">Add to cart</button>

</div>


<table>
  <tr><td>Multi-threading</td></tr>
  <tr><td>JSON Export</td></tr>
  <tr><td>Python API</td></tr>
  <tr><td>Community support</td></tr>
</table>


</div>



<!--

Batch

 -->


<div class="vboxlayout" markdown=1>
<div class="vboxlayout product salmon">

<h2 class="product">Batch</h2>
<p class="type">Non-interactive</p>
<h2 class="price">£20</h2>

<div class="spacer"></div>

<button id="get-batch">Add to cart</button>

</div>

<table>
  <tr><td>Headless</td></tr>
  <tr><td>Render farms</td></tr>
  <tr><td>Automation</td></tr>
</table>

</div>

</div>  <!-- End of node-subscription -->


<div id="floating-subscription" style="display: none" class="hboxlayout">




<!-- 


Floating

 _____          _____          _____          _____  
/     \        /     \        /     \        /     \ 
       \______/       \______/       \______/       \

-->





<!--

Apprentice

 -->


<div class="vboxlayout" markdown=1>

<div class="vboxlayout product lightblue">
<h2 class="product">Apprentice</h2>
<p class="type">Non-commercial</p>
<h2 class="price">Free</h2>
<div class="spacer"></div>
<a href="https://learn.ragdolldynamics.com/download" class="button blue text-white">Download</a>
</div>

<table>
  <tr><td>Non-commercial</td></tr>
  <tr><td>All features</td></tr>
  <tr><td>30-days trial</td></tr>
</table>

</div>


<!--

Standard

 -->


<div class="vboxlayout" markdown=1>
<div class="vboxlayout product gold">

<h2 class="product">Standard</h2>
<p class="type">Individuals</p>
<h2 class="price">£80</h2>
<div class="spacer"></div>
<button id="get-standard-floating">Add to cart</button>

</div>

<table>
  <tr><td>High-performance solver</td></tr>
  <tr><td>Artist tools</td></tr>
  <tr><td>Concurrent activations</td></tr>
  <tr><td>Community support</td></tr>
</table>

</div>


<!--

Complete

 -->


<div class="vboxlayout" markdown=1>
<div class="vboxlayout product rust">

<h2 class="product">Complete</h2>
<p class="type">Studios</p>
<h2 class="price earlybird">£80</h2>
<h2 class="price" style="text-decoration: line-through;">£215</h2>
<div class="spacer"></div>
<button id="get-complete-floating">Add to cart</button>

</div>

<table>
  <tr><td>Multi-threading</td></tr>
  <tr><td>JSON Export</td></tr>
  <tr><td>Python API</td></tr>
  <tr><td>Community support</td></tr>
</table>

</div>



<!--

Batch

 -->


<div class="vboxlayout" markdown=1>
<div class="vboxlayout product salmon">

<h2 class="product">Batch</h2>
<p class="type">Non-interactive</p>
<h2 class="price">£30</h2>

<div class="spacer"></div>

<button id="get-batch-floating">Add to cart</button>

</div>

<table>
  <tr><td>Headless</td></tr>
  <tr><td>Render farms</td></tr>
  <tr><td>Automation</td></tr>
</table>

</div>

</div> <!-- End of floating-subscription -->






</div>

</section>




<!-- 


Early Bird


-->


<section class=earlybird markdown=1>

<div class="backdrop backdrop3"></div>

<div class="vboxlayout align-center">
<!-- <img width=600 src=https://user-images.githubusercontent.com/2152766/119231842-b4b16300-bb1a-11eb-8476-9ffb6ae7bc33.png> -->
<!-- <img width=600 src=https://user-images.githubusercontent.com/2152766/119233429-ed543b00-bb20-11eb-865b-23adf1a12f93.png> -->
<!-- <img width=600 src=https://user-images.githubusercontent.com/2152766/119233574-b03c7880-bb21-11eb-9b3e-495ba995dc04.png> -->
<img width=600 src=https://user-images.githubusercontent.com/2152766/119258058-fb0ccd80-bbbf-11eb-8025-80e08241cd0d.png>

<p id="description" class="large-font text-white">
For a <i>limited time</i>, all <b>Complete</b> licences
<br>are provided at the cost of <b>Standard</b> licences.
</p>

</div>

</section>


<!-- 


 ____               _______
|          /\      /       \
|         /  \     |       |
|--      /____\    |       |
|       /      \   |       |
|      /        \  \__/____/
                     /


-->



<section class=faq markdown=1>

<div class="margin-center" markdown=1>

## FAQ

Let's dive into specifics.

</div>

<div class="faq" markdown=1>

<div class="q" markdown=1>

#### How does it work?

A non-commercial licence is automatically activated upon launch, and a commercial licence can be entered manually afterwards.

<div class="spacer"></div>
<div class="hboxlayout justify-center">
    <a href="https://learn.ragdolldynamics.com/licencing/#how-does-it-work" class="button lightgreen">Read more</a>
</div>

</div>






<div class="q" markdown=1>

#### What happens when my trial expires?

Ragdoll will simply stop simulating. Nothing else is affected and you can safely keep on doing non-Ragdoll things.

<div class="spacer"></div>
<div class="hboxlayout justify-center">
    <a href="https://learn.ragdolldynamics.com/licencing/#how-does-it-work" class="button salmon">Then what?</a>
</div>

</div>




<div class="q" markdown=1>

#### Can I mix commercial and non-commercial scenes?

**No**. A scene saved with a non-commerial licence won't open with a commercial licence.

<div class="spacer"></div>
<div class="hboxlayout justify-center">
    <a href="https://learn.ragdolldynamics.com/licencing/#how-does-it-work" class="button gold">Why not?</a>
</div>

</div>





<div class="q" markdown=1>


#### Can I use my licence on more than one machine?

**Yes**. With a Standard licence.

<div class="spacer"></div>
<div class="hboxlayout justify-center">
    <a href="https://learn.ragdolldynamics.com/licencing/#how-does-it-work" class="button rust">Tell me more</a>
</div>

</div>





<div class="q" markdown=1>


#### Can I move a licence between two machines?

**Yes**. Activation and deactivation is instant and is based on the physical machine, rather than location or project.

<div class="spacer"></div>
<div class="hboxlayout justify-center">
    <a href="https://learn.ragdolldynamics.com/licencing/#do-i-need-an-internet-connection-to-use-ragdoll" class="button lightblue">Tell me more</a>
</div>

</div>





<div class="q" markdown=1>

#### Do I need an internet connection to use Ragdoll?

**No**. But it does simplify the activation process.

<div class="spacer"></div>
<div class="hboxlayout justify-center">
    <a href="https://learn.ragdolldynamics.com/licencing/#how-does-it-work" class="button salmon">Tell me more</a>
</div>

</div>





<div class="q" markdown=1>

#### How does floating licences work?

Floating licences have an additional server you need running on your premises. Have a look at the documentation for details.

<div class="spacer"></div>
<div class="hboxlayout justify-center">
    <a href="https://learn.ragdolldynamics.com/licencing/#how-does-it-work" class="button lightgreen">Floating Documentation</a>
</div>

</div>





<div class="q" markdown=1>

#### Can I activate offline?

**Yes**. An email transaction back and forth, and you're done.

<div class="spacer"></div>
<div class="hboxlayout justify-center">
    <a href="https://learn.ragdolldynamics.com/licencing/#offline-activation" class="button rust">Offline Activation</a>
</div>

</div>




<div class="q" markdown=1>

#### When exactly is internet required?

Typically on plug-in load, but at the very latest whenever a simulation is about to begin. That is, when you hit play.

<div class="spacer"></div>
<div class="hboxlayout justify-center">
    <a href="https://learn.ragdolldynamics.com/licencing/#how-does-it-work" class="button gold">Tell me more</a>
</div>

</div>


</div>

<div class="backdrop backdrop4"></div>
</section>

