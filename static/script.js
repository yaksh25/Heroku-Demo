document.addEventListener("DOMContentLoaded", function() {
  const addBtn = document.querySelector("#multiple-datasets-container .add");
  const input = document.querySelector("#multiple-datasets-container .inp-group");

  function removeInput() {
    this.parentElement.remove();
  }

  function addInput() {
    const col = document.createElement("input");
    col.type = "text";
    col.placeholder = "Enter header";
    col.name = "selectedMValues[]";

    const name = document.createElement("input");
    name.type = "number";
    name.placeholder = "From";
    name.name = "from";

    const to = document.createElement("input");
    to.type = "number";
    to.placeholder = "To";
    to.name = "to";

    const colh = document.createElement("input");
    colh.type = "text";
    colh.placeholder = "Enter column header";
    colh.name = "colh"

    const rowc = document.createElement("input");
    rowc.type = "number";
    rowc.placeholder = "Enter row cell";
    rowc.name = "rowc"
   

    const btn = document.createElement("a");
    btn.className = "delete";
    btn.innerHTML = "&times";
    btn.addEventListener("click", removeInput);

    const flex = document.createElement("div");
    flex.className = "flex";

    input.appendChild(flex);
    flex.appendChild(col);
    flex.appendChild(name);
    flex.appendChild(to);
    flex.appendChild(colh);
    flex.appendChild(rowc);
    flex.appendChild(btn);

  }

  addBtn.addEventListener("click", addInput);

  // Handle file upload form submission
  document.querySelector("form").addEventListener("submit", function(e) {
    e.preventDefault(); // Prevent the default form submission

    // Perform an AJAX POST request to the /upload route
    const formData = new FormData(this);
    fetch("/upload", {
      method: "POST",
      body: formData,
    })
      .then(response => response.json())
      .then(data => {
        // Handle the received data
        console.log(data);
        // Use the data as needed
        var select = document.getElementById("columns-select");
        for (var i = 0; i < data.columns.length; i++) {
          select.options[i] = new Option(data.columns[i], data.columns[i]);
        }
      })
      .catch(error => {
        // Handle any errors
        console.error('Error:', error);
      });
  });

  const selectBtn = document.querySelector(".select-btn");
  const items = document.querySelectorAll(".item");
  items.forEach(item => {
    item.addEventListener("click", () => {
      item.classList.toggle("checked");
      let checked = document.querySelectorAll(".checked");
      let btnText = document.querySelector(".btn-text");
      if (checked && checked.length > 0) {
        btnText.innerText = `${checked.length} Selected`;
      } else {
        btnText.innerText = "Select Language";
      }
    });
  });

  // Add event listener to save the values when the form is submitted
  document.querySelector(".btn-secondary").addEventListener("click", function(event) {
    event.preventDefault();
    saveValues();
  });

  function saveValues() {
    const formData = new FormData();

    const inputs = document.querySelectorAll(".flex input");
    inputs.forEach(function(input) {
      if (input.name === "from" || input.name === "to") {
        formData.append(input.name, input.value);
      } else if (input.name === "colh") {
        formData.append('colh', input.value);
      } else if (input.name === "rowc") {
        formData.append('rowc', input.value);
      }
      else {
        formData.append('selectedMValues[]', input.value);
      }
    });

    fetch("/upload", {
      method: "POST",
      body: formData
    })
      .then(response => response.json())
      .then(data => {
        console.log(data.message);
      })
      .catch(error => {
        console.log(error);
      });
  }
});