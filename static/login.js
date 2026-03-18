document.getElementById("loginForm").addEventListener("submit", function(e){

e.preventDefault();

let userType = document.getElementById("userType").value;

if(userType === "free"){
    window.location.href = "free-dashboard.html";
}
else{
    window.location.href = "premium-dashboard.html";
}

});