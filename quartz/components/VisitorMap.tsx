import { QuartzComponent, QuartzComponentConstructor } from "./types"

const VisitorMap: QuartzComponent = () => {
  return <body>
    <script type="text/javascript" id="clustrmaps" src="//clustrmaps.com/map_v2.js?d=1UBnJzfBqND8LMv6DAkx3at6WX_TFZn5F5Ksu9V3IAw&cl=ffffff&w=a"></script>
    <br></br>
  </body>
}

export default (() => VisitorMap) satisfies QuartzComponentConstructor