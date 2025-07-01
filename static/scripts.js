
window.onload = function () {

    let grows = document.getElementsByClassName("grow-container")

    if (grows.length > 0) {

        togglePopupMenu(grows[0].id);
    }

}

function togglePopupMenu(div_id)
{
    const element = document.getElementById(div_id);
    const currentDisplay = window.getComputedStyle(element).display;

    if (currentDisplay === "none") {
        element.style.display = "block"; // Show
    } else {
        element.style.display = "none"; // Hide
    }    
}

function scheduleCheckboxChanged(effector_id){
    schedule_checkbox = document.getElementById('schedule-checkbox-' + effector_id)
    bound_checkbox = document.getElementById('bound-checkbox-' + effector_id)
    on_time_field = document.getElementById('on-time-' + effector_id)
    off_time_field = document.getElementById('off-time-' + effector_id)

    


    if(schedule_checkbox.checked){
        bound_checkbox.checked = false;
        bound_checkbox.disabled = true;

        on_time_field.disabled = false;
        off_time_field.disabled = false;

    } else {
        bound_checkbox.disabled = false;

        on_time_field.disabled = true;
        off_time_field.disabled = true;
    }
}

function boundCheckboxChanged(effector_id){
    schedule_checkbox = document.getElementById('schedule-checkbox-' + effector_id)
    bound_checkbox = document.getElementById('bound-checkbox-' + effector_id)

    sensor_id_field = document.getElementById('bounded-sensor-id-' + effector_id)
    threshold_field = document.getElementById('threshold-' + effector_id)


    if(bound_checkbox.checked){
        schedule_checkbox.checked = false;
        schedule_checkbox.disabled = true;

        sensor_id_field.disabled = false;
        threshold_field.disabled = false;
    } else {
        schedule_checkbox.disabled = false;

        sensor_id_field.disabled = true;
        threshold_field.disabled = true;
    }
}
