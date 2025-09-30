import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import style from "./styles/footer.scss"
import { version } from "../../package.json"
import { i18n } from "../i18n"

interface Options {
  links: Record<string, string>
}

export default ((opts?: Options) => {
  const Footer: QuartzComponent = ({ displayClass, cfg }: QuartzComponentProps) => {
    const year = new Date().getFullYear()
    const links = opts?.links ?? []
    const beianImageDefaultPath = `/static/beian.png`
    return (
      <footer class={`${displayClass ?? ""}`}>
        {/* <script type="text/javascript" id="clustrmaps" src="//clustrmaps.com/map_v2.js?d=1UBnJzfBqND8LMv6DAkx3at6WX_TFZn5F5Ksu9V3IAw&cl=ffffff&w=a"></script> */}
        <p>
          <a href="https://beian.miit.gov.cn/" target="_blank">渝ICP备2025068702号-1</a>&nbsp;&nbsp;&nbsp;
          <img src={beianImageDefaultPath} alt="备案图标" height={20} style={{ margin: "0" }}></img><a href="https://beian.mps.gov.cn/#/query/webSearch?code=50010102001421" rel="noreferrer" target="_blank">渝公网安备50010102001421号</a>
        </p>
        <p>
          {i18n(cfg.locale).components.footer.createdWith}{" "}
          <a href="https://quartz.jzhao.xyz/">Quartz v{version}</a> © {year}
        </p>
        <ul>
          {Object.entries(links).map(([text, link]) => (
            <li>
              <a href={link}>{text}</a>
            </li>
          ))}
        </ul>
      </footer>
    )
  }

  Footer.css = style
  return Footer
}) satisfies QuartzComponentConstructor
