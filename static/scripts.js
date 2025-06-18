function togglePopupMenu(div_id)
{
    console.log("toggle menu");
    const element = document.getElementById(div_id);

    if (element.style.display === "none") {
        element.style.display = "block"; // Show
    } else {
        element.style.display = "none"; // Hide
    }    
}