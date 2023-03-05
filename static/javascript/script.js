const emission_selected = document.getElementById('type') 
displayUnits = function() {
    console.log(emission_selected)
    console.log(emission_selected.value)
    const units_span = document.getElementById('units_span')
    units_span.innerText = emission_selected.value
    switch(emission_selected.value) {
        case 'Electricity (VIC)':
            units_span.innerText = 'kWh';
            break;
        case 'Natural Gas':
            units_span.innerText = 'MJ';
            break;
        case 'Other':
            units_span.innerText = 'g co2'
            break;
        case 'Offset':
            units_span.innerText = 'g co2'
            break;
        default:
            units_span.innerText = 'km'
    }
}
window.onload = displayUnits() 
emission_selected.addEventListener('change', displayUnits)
// window.onload = displayUnits() 
// emission_selected.addEventListener('click', displayUnits)
// todo make this function run whenver dropdown list changes