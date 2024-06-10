function initGallery() 
{
  var plants = document.getElementsByClassName('plant-div');
  var selected_plant_label = document.getElementById('selected_plant');
  var text = '0 / 0'

  if (plants.length > 0) 
  {
    plants.item(0).style.display = "block";
    text = `1 / ${plants.length}`
    console.log(text)
  }
  
  selected_plant_label.innerHTML = text
}

function nextPlant() 
{
  var plants = document.getElementsByClassName('plant-div');
  var selected_plant_label = document.getElementById('selected_plant');
  var selected_plant = null;
  var text = '0 / 0'

  if (plants.length > 0) 
  {
    for (let index = 0; index < plants.length; index++) 
    {
      plant = plants.item(index)

      if(plant.style.display != "none")
      {
        selected_plant = index;
        break;
      }
    }

    if(selected_plant == null)
    {
      selected_plant = 0
      plants.item(0).style.display = "block"
    }
    else 
    {
      plants.item(selected_plant).style.display = "none";
      
      if (selected_plant < plants.length - 1)
      {
        selected_plant = selected_plant + 1;

        plants.item(selected_plant).style.display = "block";
        text = `${selected_plant + 1} / ${plants.length}`
      }
      else 
      {
        text = `1 / ${plants.length}`
        plants.item(0).style.display = "block";
      }
    }
  }

  selected_plant_label.innerHTML = text
}

function previousPlant() 
{
  var plants = document.getElementsByClassName('plant-div');
  var selected_plant_label = document.getElementById('selected_plant');
  var selected_plant = null;
  var text = '0 / 0'

  if (plants.length > 0) 
  {
    for (let index = 0; index < plants.length; index++) 
    {
      plant = plants.item(index);

      if(plant.style.display != "none")
      {
        selected_plant = index;
        break;
      }
    }

    if(selected_plant == null)
    {
      plants.item(0).style.display = "block";
    }
    else 
    {
      if (selected_plant != 0) 
      {
        plants.item(selected_plant).style.display = "none";

        selected_plant = selected_plant - 1;

        plants.item(selected_plant).style.display = "block";
        text = `${selected_plant + 1} / ${plants.length}`
      }
      else{
        text = `1 / ${plants.length}`
      }
    }
  }

  selected_plant_label.innerHTML = text
}

function showTab(tab) 
{

}


