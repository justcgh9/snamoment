// function openLogin() {
//     var blurOverlay = document.querySelector('.blur-overlay');
//     var loginPage = window.open('login.html', '_blank', 'width=400,height=300');
    
//     blurOverlay.style.display = 'block';
//     loginPage.focus();
//   }
//get all dropdowns
// const dropdowns = document.querySelectorAll('.dropdown');
// dropdowns.forEach(dropdown => {
//     const select = dropdown.querySelector('.select');
//     const caret = dropdown.querySelector('.caret');
//     const menu = dropdown.querySelector('.menu');
//     const options = dropdown.querySelectorAll('.menu li');
//     const selected = dropdown.querySelector('.selected');
//     select.addEventListener('click', () => {
//         select.classList.toggle('select-clicked');
//         caret.classList.toggle('caret-rotate');
//         menu.classList.toggle('menu-open');
//     });
//     options.forEach(option => {
//         option.addEventListener('click', () => {
//             selected.innerText = option.innerText;
//             select.classList.remove('select-clicked');
//             caret.classList.remove('caret-rotate');
//             menu.classList.remove('menu-open');

//             options.forEach(option => {
//                 option.classList.remove('active');
//             });
//             option.classList.add('active');
//         });
//     });
// });
// const optionMenu = document.querySelector(".select-menu");
// const selectBtn = document.querySelector(".select-btn");
// const options = document.querySelectorAll(".option");
// const sBtn_text = document.querySelector(".sBtn-text");
// options.forEach(option =>{
//     option.addEventListener("click", () =>{
//         let selectedOption = option.querySelector(".option-text").innerText;
//         sBtn_text.innerText = selectedOption;
//         console.log(selectedOption);
//     })
// });
// const optionMenu = document.querySelector(".select-menu");
// const selectBtn = document.querySelector(".select-btn");
// const options = document.querySelectorAll(".option");
// const sBtn_text = document.querySelector(".sBtn-text");

// selectBtn.addEventListener("click", () => {
//   optionMenu.classList.toggle("active");
// });

// options.forEach((option) => {
//   option.addEventListener("click", () => {
//     let selectedOption = option.querySelector(".option-text").innerText;
//     sBtn_text.innerText = selectedOption;
//     console.log(selectedOption);
//     optionMenu.classList.remove("active");
//   });
// });
// document.addEventListener("DOMContentLoaded", function() {
//     function show(value) {
//       document.querySelector(".text-box").value = value;
//     }
  
//     let dropdown = document.querySelector(".dropdown");
//     dropdown.onclick = function() {
//       dropdown.classList.toggle("active");
//     };
//   });
  
document.addEventListener("DOMContentLoaded", function() {
    function show(value) {
      document.querySelector(".text-box").value = value;
    }
  
    let dropdowns = document.querySelectorAll(".dropdown");
    dropdowns.forEach(function(dropdown) {
      dropdown.onclick = function() {
        this.classList.toggle("active");
      };
    });
  });
  // const fileUploader = document.getElementById('file-upload');
  // fileUploader.addEventListener('change', (event) => {
  //   const files = event.target.files;
  //   console.log('files', files);
  // });

  function updateFileName(input) {
    var fileName = input.value.split("\\").pop(); // Extract file name from input value
    document.getElementById("file-name").value = fileName; // Update file name in the text input field
  }
  
 const buttonElem = document.querySelector('.upload');
 const modalElem = document.querySelector('.modal');

 modalElem.style.cssText = `
      display: flex;
      visibility: hidden;
      opacity: 0;
      transition: opacity 300ms ease-in-out;
 `;

 const closeModal = event => {
    const target = event.target;

    if (target == modalElem || target.closest('.modal__close')) {
      modalElem.style.visibility = 'hidden';
      modalElem.style.opacity = 0;

      setTimeout(() => {
        modalElem.style.visibility = 'hidden';
      }, 300)
    }
 }

 const openModal = () => {
    modalElem.style.visibility = 'visible';
    modalElem.style.opacity = 1;
 };
 buttonElem.addEventListener('click', openModal);
 modalElem.addEventListener('click', closeModal)