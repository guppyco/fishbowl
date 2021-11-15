const bubbleCount = 30;
const bubbleField = document.getElementById('bubble-field');

//generate bubbles with randomly timed animation durations
for (i = 0; i < bubbleCount; i++) {
  const randNum = Math.floor(Math.random() * 20) + 1;
  const animDur = 3 + (randNum);
  moveEl = document.createElement('div');
  moveEl.setAttribute('class', 'bubble-rise');
  moveEl.setAttribute('style', 'animation-duration: ' + animDur + 's;');

  bubbleEl = document.createElement('div');
  bubbleEl.setAttribute('class', 'bubble');
  bubbleElContent = document.createTextNode('');
  bubbleEl.appendChild(bubbleElContent);

  moveEl.appendChild(bubbleEl)
  bubbleField.appendChild(moveEl);
}
