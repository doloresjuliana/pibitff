<template>
    <div class="wrapper">
        <div class="one">
            <iframe class="w-full min-w-[75vw] h-[90vh]" 
            src="http://192.168.1.65:8000/private/files/FACTURA%20230421.pdf">
            </iframe>
        </div>
        <div class="two">Two
            <h1>Aqui 2</h1>
        </div>
    </div>
</template>
<script setup></script>

<style lang="scss" scoped>
.wrapper {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-gap: 10px;
  grid-auto-rows: minmax(100px, auto);
}
.one {
  background-color: blueviolet;
  grid-column: 1 / 2;
}
.two {
  background-color: blue;
  grid-column: 2 / 2;
}
</style>