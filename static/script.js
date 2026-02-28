// Grab the elements from the HTML
const mainForm = document.getElementById('mainForm');
const modal = document.getElementById('previewModal');

// 1. INTERCEPT THE FORM SUBMISSION
mainForm.addEventListener("submit", function(e) {
    // Stop the form from sending data to Python immediately
    e.preventDefault(); 

    // Get the values the user typed into the inputs
    const nameValue = document.getElementById("student_name").value;
    const posValue = document.getElementById("position").value;

    // Inject those values into the Preview Modal text
    document.getElementById("previewName").innerText = nameValue;
    document.getElementById("previewPosition").innerText = posValue;

    // Make the Modal visible
    modal.style.display = "flex";
    
    console.log("Showing preview for: " + nameValue);
});

// 2. FUNCTION TO CLOSE THE MODAL (If they clicked "Edit")
function closePreview() {
    modal.style.display = "none";
}

// 3. FUNCTION FOR FINAL DOWNLOAD
function submitFinal() {
    const confirmBtn = document.querySelector(".btn-confirm");
    
    // Change button appearance to show it's working
    confirmBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
    confirmBtn.style.background = "#95a5a6";
    confirmBtn.disabled = true;

    // Actually submit the form to the Python /generate route
    mainForm.submit();

    // Hide the modal after a short delay so the user can start over
    setTimeout(() => {
        modal.style.display = "none";
        // Reset the button for the next use
        confirmBtn.innerHTML = 'Download Certificate <i class="fas fa-download"></i>';
        confirmBtn.style.background = "#27ae60"; 
        confirmBtn.disabled = false;
    }, 4000);
}