<!DOCTYPE html>
<html>
<head>
<title>Edit Subscription Plans Section</title>
<style>
body{
    margin:0;
    font-family:Arial, sans-serif;
    background:#f5f6f8;
}
.topbar{
    height:70px;
    background:rgba(131,198,255,0.5);
    display:flex;
    align-items:center;
    justify-content:space-between;
    padding:0 18px;
    box-sizing:border-box;
}
.topbarLeft{
    font-size:22px;
    font-weight:bold;
    line-height:1.05;
}
.topbarRight{
    display:flex;
    align-items:center;
    gap:12px;
    font-weight:bold;
}
.profileIcon{
    width:38px;
    height:38px;
    border-radius:50%;
    background:#d9dcec;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:20px;
}
.layout{
    display:flex;
    min-height:calc(100vh - 70px);
}
.sidebar{
    width:310px;
    background:#f1f2f4;
    padding:24px 20px;
    box-sizing:border-box;
    border-right:1px solid #e5e7eb;
}
.profileCard{
    background:#f7f8fb;
    border-radius:16px;
    padding:24px 20px;
    display:flex;
    align-items:center;
    gap:18px;
    margin-bottom:28px;
}
.profileAvatar{
    width:56px;
    height:56px;
    border-radius:50%;
    background:#d9dcec;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:28px;
}
.profileText1{
    font-size:16px;
    font-weight:bold;
}
.profileText2{
    font-size:14px;
}
.menuItem{
    display:flex;
    align-items:center;
    gap:14px;
    padding:14px 16px;
    border-radius:12px;
    margin-bottom:10px;
    font-size:18px;
    font-weight:600;
    cursor:pointer;
}
.activeMenu{
    background:#e4e7f2;
}
.main{
    flex:1;
    padding:24px 30px 40px 30px;
}
.menuToggle{
    font-size:32px;
    margin-bottom:18px;
}
.breadcrumb{
    font-size:14px;
    margin-bottom:28px;
}
.breadcrumb a{
    color:#3b82c4;
    text-decoration:none;
}
.pageTitle{
    font-size:28px;
    font-weight:bold;
    margin-bottom:34px;
}
.label{
    font-size:18px;
    font-weight:bold;
    margin-bottom:12px;
}
.inputBox{
    width:260px;
    height:40px;
    border:1px solid #d7dbe8;
    background:#eef0fb;
    border-radius:8px;
    margin-bottom:34px;
    padding:10px 12px;
    box-sizing:border-box;
    font-size:15px;
}
.textbox{
    width:460px;
    height:150px;
    border:1px solid #d7dbe8;
    background:#eef0fb;
    border-radius:8px;
    margin-bottom:28px;
    padding:14px;
    box-sizing:border-box;
    font-size:15px;
    resize:none;
}
.buttonRow{
    margin-top:48px;
    display:flex;
    gap:28px;
}
.cancelBtn{
    border:none;
    border-radius:8px;
    background:#d9d9d9;
    padding:12px 24px;
    font-size:16px;
    font-weight:bold;
    cursor:pointer;
}
.saveBtn{
    border:none;
    border-radius:8px;
    background:#1683ff;
    color:white;
    padding:12px 24px;
    font-size:16px;
    font-weight:bold;
    cursor:pointer;
}
</style>
</head>
<body>

<div class="topbar">
    <div class="topbarLeft">Daily Scoop News<br>System</div>
    <div class="topbarRight">
        <div class="profileIcon">👤</div>
        <div>Hi, Username</div>
        <div onclick="window.location.href='/logout'" style="cursor:pointer;">Logout</div>
    </div>
</div>

<div class="layout">
    <div class="sidebar">
        <div class="profileCard">
            <div class="profileAvatar">👤</div>
            <div>
                <div class="profileText1">Username</div>
                <div class="profileText2">Role</div>
            </div>
        </div>

        <div class="menuItem" onclick="window.location.href='/admin/dashboard'">🏠 Dashboard</div>
        <div class="menuItem" onclick="window.location.href='/admin/user-accounts'">👤 User Accounts</div>
        <div class="menuItem" onclick="window.location.href='/admin/article-reported'">🚩 Article Reported</div>
        <div class="menuItem" onclick="window.location.href='/admin/category-management'">▦ Category Management</div>
        <div class="menuItem activeMenu" onclick="window.location.href='/admin/webpage-management'">🗂 Webpage Management</div>
        <div class="menuItem" onclick="window.location.href='/admin/system-monitoring'">🖥 System Monitoring</div>
        <div class="menuItem" onclick="window.location.href='/admin/auto-publish-rules'">☑ Auto-Publish Rules</div>
    </div>

    <div class="main">
        <div class="menuToggle">☰</div>
        <div class="breadcrumb">
            <a href="/admin/webpage-management">Webpage Management</a> / Edit Subscription Plans Section
        </div>

        <div class="pageTitle">Edit Subscription Plans Section</div>

        <div class="label">Plan Name</div>
        <input class="inputBox" id="planName">

        <div class="label">Plan Description</div>
        <textarea class="textbox" id="planDescription"></textarea>

        <div class="label">Price</div>
        <input class="inputBox" id="price">

        <div class="label">Billing Cycle</div>
        <input class="inputBox" id="billingCycle">

        <div class="label">Plan Status</div>
        <input class="inputBox" id="planStatus">

        <div class="buttonRow">
            <button class="cancelBtn" onclick="window.location.href='/admin/webpage-management'">Cancel</button>
            <button class="saveBtn" onclick="saveSubscriptionPlan()">Save Changes</button>
        </div>
    </div>
</div>

<script>
window.onload = loadSubscriptionPlan;

function loadSubscriptionPlan(){
    fetch("http://127.0.0.1:5000/admin/subscription-plan")
    .then(res => res.json())
    .then(data => {
        document.getElementById("planName").value = data.planName || "";
        document.getElementById("planDescription").value = data.planDescription || "";
        document.getElementById("price").value = data.price || "";
        document.getElementById("billingCycle").value = data.billingCycle || "";
        document.getElementById("planStatus").value = data.planStatus || "";
    });
}

function saveSubscriptionPlan(){
    fetch("http://127.0.0.1:5000/admin/subscription-plan", {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            planName: document.getElementById("planName").value,
            planDescription: document.getElementById("planDescription").value,
            price: document.getElementById("price").value,
            billingCycle: document.getElementById("billingCycle").value,
            planStatus: document.getElementById("planStatus").value
        })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        window.location.href = "/admin/webpage-management";
    });
}
</script>

</body>
</html>
