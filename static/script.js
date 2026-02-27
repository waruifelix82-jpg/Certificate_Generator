document.querySelector("form").addEventListeners("submit",function(e){
    const button=document.querySelector("button");
    const name=document.querySelector("input[name="name"]").value;

    button.innerText="Generating...please WakeLockSentinel";
    button.style.background="#95a5a6";
    button.disabled=true

    console.log("Generating certificate for:"+ name);

});