<template>
    <div class="wrapper">
        <iframe :src=urlpdf></iframe>
        <iframe :src=urldoctype></iframe>
    </div>
</template>

<script>
export default {
  props: {
    urlpdf: String,
    urldoctype: String
  }
}
</script>

<style lang="scss" scoped>
.wrapper {
  width: 100%;
  height: 100%;
  margin: 0px;
  display: flex;
  flex-wrap: wrap;
  background-color: DodgerBlue;
}

.wrapper > iframe{
  background-color: #f1f1f1;
  width: 49%;
  height: 480px;
  margin: 0.5%;
  line-height: 1500%;
}
</style>