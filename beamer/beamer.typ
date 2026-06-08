#import "@preview/modern-sysu-touying:0.1.0": *
#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge
#import "@preview/showybox:2.0.4": showybox

#let sysu-green = rgb("#00664f")
#let sysu-red = rgb("#8b1e2d")
#let pale-green = rgb("#eaf4f0")
#let pale-red = rgb("#f8ecee")
#let pale-gold = rgb("#fff5dc")
#let ink = rgb("#24332e")
#let muted = rgb("#60706a")
#let line = rgb("#d6e1dd")

#show: sysu-theme.with(
  lang: "zh",
  font: "Noto Sans CJK SC",
  config-common(new-section-slide-fn: none),
  config-info(
    title: [基于字符相似性与机器学习的互联网垃圾文本检测系统],
    subtitle: [规则、字符变体、TF-IDF 与 RoBERTa 融合检测实践],
    author: [雷颜玮、李巴蒂、卢嘉聪、元朗曦],
    date: [2026 年 6 月],
    institution: [中山大学],
  ),
)

#title-slide()

#outline-slide(title: [内容提要], level: 1)

= 背景与目标

== 研究背景与检测难点

#grid(
  columns: (1fr, 1fr),
  column-gutter: 18pt,
  [
    #text(size: 16pt, weight: "bold", fill: sysu-green)[垃圾文本正在主动“伪装”]
    #v(9pt)
    #showybox(
      title: text(size: 17pt, weight: "bold", fill: sysu-red)[形近字替换],
      frame: (
        title-color: pale-red,
        body-color: pale-red,
        border-color: sysu-red,
        radius: 7pt,
        thickness: 1pt,
        title-inset: (left: 12pt, right: 12pt, top: 8pt, bottom: 8pt),
        body-inset: (left: 12pt, right: 12pt, top: 2pt, bottom: 10pt),
      ),
      title-style: (sep-thickness: 0pt),
      spacing: 0pt,
      [#text(size: 12.5pt, fill: ink)[“加微信”写成“加薇信”，绕过精确关键词匹配。]],
    )
    #v(8pt)
    #showybox(
      title: text(size: 17pt, weight: "bold", fill: sysu-green)[缩写与混写],
      frame: (
        title-color: pale-green,
        body-color: pale-green,
        border-color: sysu-green,
        radius: 7pt,
        thickness: 1pt,
        title-inset: (left: 12pt, right: 12pt, top: 8pt, bottom: 8pt),
        body-inset: (left: 12pt, right: 12pt, top: 2pt, bottom: 10pt),
      ),
      title-style: (sep-thickness: 0pt),
      spacing: 0pt,
      [#text(size: 12.5pt, fill: ink)[使用 `vx`、`wx`、数字和外语片段隐藏联系方式。]],
    )
    #v(8pt)
    #showybox(
      title: text(size: 17pt, weight: "bold", fill: rgb("#a36a00"))[分隔符插入],
      frame: (
        title-color: pale-gold,
        body-color: pale-gold,
        border-color: rgb("#a36a00"),
        radius: 7pt,
        thickness: 1pt,
        title-inset: (left: 12pt, right: 12pt, top: 8pt, bottom: 8pt),
        body-inset: (left: 12pt, right: 12pt, top: 2pt, bottom: 10pt),
      ),
      title-style: (sep-thickness: 0pt),
      spacing: 0pt,
      [#text(size: 12.5pt, fill: ink)[“领·取”“私 聊”“扫 码”等写法破坏连续文本特征。]],
    )
  ],
  [
    #block(
      width: 100%,
      fill: ink,
      radius: 12pt,
      inset: 18pt,
      [
        #text(size: 12pt, fill: white.lighten(18%))[典型变体文本]
        #v(12pt)
        #text(size: 23pt, weight: "bold", fill: white)[
          加 薇 信 领·取 优 惠
        ]
        #v(16pt)
        #std.line(length: 100%, stroke: 1pt + white.transparentize(65%))
        #v(14pt)
        #text(size: 13pt, fill: white)[
          单一关键词规则难以兼顾召回率与误报率；单一统计模型也难以覆盖持续变化的对抗写法。
        ]
      ],
    )
    #v(12pt)
    #align(center)[
      #text(size: 17pt, weight: "bold", fill: sysu-red)[核心挑战]
      #v(3pt)
      #text(size: 14pt, fill: ink)[识别语义意图，而不只匹配表面字符]
    ]
  ],
)

== 项目目标与总体方案

#align(center)[
  #text(size: 20pt, weight: "bold", fill: ink)[构建一个面向真实互联网文本的多语言垃圾检测系统]
]
#v(13pt)

#grid(
  columns: (1fr, 1fr, 1fr),
  column-gutter: 12pt,
  showybox(
    title: text(size: 17pt, weight: "bold", fill: sysu-green)[多语言分类],
    frame: (
      title-color: pale-green,
      body-color: pale-green,
      border-color: sysu-green,
      radius: 7pt,
      thickness: 1pt,
      title-inset: (left: 12pt, right: 12pt, top: 8pt, bottom: 8pt),
      body-inset: (left: 12pt, right: 12pt, top: 2pt, bottom: 10pt),
    ),
    title-style: (sep-thickness: 0pt),
    spacing: 0pt,
    [#text(size: 12.5pt, fill: ink)[结合传统机器学习与多语言 RoBERTa，对中文、英文等文本完成正常 / 垃圾二分类。]],
  ),
  showybox(
    title: text(size: 17pt, weight: "bold", fill: sysu-red)[风险量化],
    frame: (
      title-color: pale-red,
      body-color: pale-red,
      border-color: sysu-red,
      radius: 7pt,
      thickness: 1pt,
      title-inset: (left: 12pt, right: 12pt, top: 8pt, bottom: 8pt),
      body-inset: (left: 12pt, right: 12pt, top: 2pt, bottom: 10pt),
    ),
    title-style: (sep-thickness: 0pt),
    spacing: 0pt,
    [#text(size: 12.5pt, fill: ink)[将规则、字符变体与模型概率统一为 0–1 风险分数，支持阈值调整。]],
  ),
  showybox(
    title: text(size: 17pt, weight: "bold", fill: rgb("#a36a00"))[可解释输出],
    frame: (
      title-color: pale-gold,
      body-color: pale-gold,
      border-color: rgb("#a36a00"),
      radius: 7pt,
      thickness: 1pt,
      title-inset: (left: 12pt, right: 12pt, top: 8pt, bottom: 8pt),
      body-inset: (left: 12pt, right: 12pt, top: 2pt, bottom: 10pt),
    ),
    title-style: (sep-thickness: 0pt),
    spacing: 0pt,
    [#text(size: 12.5pt, fill: ink)[返回命中关键词、链接、联系方式、变体写法及各模块分数。]],
  ),
)

#v(18pt)
#align(center)[
  #diagram(
    spacing: (8mm, 0mm),
    node-inset: 8pt,
    edge-stroke: 1.2pt + sysu-green,
    node(
      (0, 0),
      align(center)[
        #text(size: 13pt, weight: "bold", fill: sysu-green)[输入文本]
        #linebreak()
        #text(size: 8pt, fill: muted)[评论 / 短信 / 广告]
      ],
      width: 39mm,
      height: 17mm,
      fill: white,
      stroke: 1.2pt + sysu-green,
      corner-radius: 7pt,
    ),
    edge((0, 0), (1, 0), "->"),
    node(
      (1, 0),
      align(center)[
        #text(size: 13pt, weight: "bold", fill: sysu-red)[多路检测]
        #linebreak()
        #text(size: 9pt, fill: muted)[规则 + 变体 + 双模型]
      ],
      width: 39mm,
      height: 17mm,
      fill: pale-red,
      stroke: 1.2pt + sysu-red,
      corner-radius: 7pt,
    ),
    edge((1, 0), (2, 0), "->"),
    node(
      (2, 0),
      align(center)[
        #text(size: 13pt, weight: "bold", fill: sysu-green)[分数融合]
        #linebreak()
        #text(size: 9pt, fill: muted)[统一风险评分]
      ],
      width: 39mm,
      height: 17mm,
      fill: pale-green,
      stroke: 1.2pt + sysu-green,
      corner-radius: 7pt,
    ),
    edge((2, 0), (3, 0), "->"),
    node(
      (3, 0),
      align(center)[
        #text(size: 13pt, weight: "bold", fill: sysu-red)[检测结果]
        #linebreak()
        #text(size: 9pt, fill: muted)[标签 + 原因 + 概率]
      ],
      width: 39mm,
      height: 17mm,
      fill: pale-red,
      stroke: 1.2pt + sysu-red,
      corner-radius: 7pt,
    ),
  )
]

= 数据与检测方法

== 数据集与处理流程

#grid(
  columns: (0.82fr, 1.18fr),
  column-gutter: 18pt,
  [
    #showybox(
      title: text(size: 17pt, weight: "bold", fill: sysu-green)[传统模型数据],
      frame: (
        title-color: pale-green,
        body-color: pale-green,
        border-color: sysu-green,
        radius: 7pt,
        thickness: 1pt,
        title-inset: (left: 12pt, right: 12pt, top: 8pt, bottom: 8pt),
        body-inset: (left: 12pt, right: 12pt, top: 2pt, bottom: 10pt),
      ),
      title-style: (sep-thickness: 0pt),
      spacing: 0pt,
      [
        #text(size: 12.5pt, fill: ink)[
          #text(size: 25pt, weight: "bold", fill: sysu-green)[2,400]
          #linebreak()
          小规模标注文本，用于训练 TF-IDF/LR 基线并快速验证完整流程。
        ]
      ],
    )
    #v(10pt)
    #showybox(
      title: text(size: 17pt, weight: "bold", fill: sysu-red)[RoBERTa 数据],
      frame: (
        title-color: pale-red,
        body-color: pale-red,
        border-color: sysu-red,
        radius: 7pt,
        thickness: 1pt,
        title-inset: (left: 12pt, right: 12pt, top: 8pt, bottom: 8pt),
        body-inset: (left: 12pt, right: 12pt, top: 2pt, bottom: 10pt),
      ),
      title-style: (sep-thickness: 0pt),
      spacing: 0pt,
      [
        #text(size: 12.5pt, fill: ink)[
          #text(size: 25pt, weight: "bold", fill: sysu-red)[百万条级别]
          #linebreak()
          汇总多个公开垃圾文本数据源，覆盖中文、英文等 23 种语言。
        ]
      ],
    )
  ],
  [
    #align(center)[
      #text(size: 16pt, weight: "bold", fill: sysu-green)[统一数据处理管线]
      #v(10pt)
      #diagram(
        spacing: (8mm, 6mm),
        edge-stroke: 1.1pt + sysu-green,
        node(
          (0, 0),
          align(center)[
            #text(size: 11pt, weight: "bold", fill: sysu-green)[多源采集]
            #linebreak()
            #text(size: 6.8pt, fill: muted)[5 个公开数据源]
          ],
          width: 36mm,
          height: 16mm,
          fill: white,
          stroke: 1pt + sysu-green,
          corner-radius: 6pt,
        ),
        edge((0, 0), (1, 0), "->"),
        node(
          (1, 0),
          align(center)[
            #text(size: 11pt, weight: "bold", fill: sysu-green)[格式统一]
            #linebreak()
            #text(size: 6.8pt, fill: muted)[text / label / language]
          ],
          width: 36mm,
          height: 16mm,
          fill: pale-green,
          stroke: 1pt + sysu-green,
          corner-radius: 6pt,
        ),
        edge((1, 0), (1, 1), "->"),
        node(
          (1, 1),
          align(center)[
            #text(size: 11pt, weight: "bold", fill: sysu-red)[清洗去重]
            #linebreak()
            #text(size: 6.8pt, fill: muted)[移除空值与重复样本]
          ],
          width: 36mm,
          height: 16mm,
          fill: pale-red,
          stroke: 1pt + sysu-red,
          corner-radius: 6pt,
        ),
        edge((1, 1), (0, 1), "->"),
        node(
          (0, 1),
          align(center)[
            #text(size: 11pt, weight: "bold", fill: sysu-red)[训练划分]
            #linebreak()
            #text(size: 6.8pt, fill: muted)[训练集 / 验证集]
          ],
          width: 36mm,
          height: 16mm,
          fill: pale-red,
          stroke: 1pt + sysu-red,
          corner-radius: 6pt,
        ),
      )
      #v(12pt)
      #block(
        fill: pale-gold,
        stroke: 0.8pt + rgb("#d9b45b"),
        radius: 7pt,
        inset: 10pt,
        [
          #text(size: 12pt, weight: "bold", fill: rgb("#7a5500"))[统一标签：]
          #text(size: 12pt, fill: ink)[ `ham = 0`，`spam = 1`；训练前完成随机化与去重。]
        ],
      )
    ]
  ],
)

== 规则与字符变体检测

#grid(
  columns: (1fr, 1fr),
  column-gutter: 18pt,
  [
    #text(size: 16pt, weight: "bold", fill: sysu-green)[可解释规则层]
    #v(8pt)
    #grid(
      columns: (1fr, 1fr),
      column-gutter: 8pt,
      row-gutter: 8pt,
      showybox(
        title: text(size: 15pt, weight: "bold", fill: sysu-green)[链接],
        frame: (
          title-color: pale-green,
          body-color: pale-green,
          border-color: sysu-green,
          radius: 7pt,
          thickness: 1pt,
          title-inset: (left: 10pt, right: 10pt, top: 7pt, bottom: 8pt),
          body-inset: (left: 10pt, right: 10pt, top: 1pt, bottom: 8pt),
        ),
        title-style: (sep-thickness: 0pt),
        spacing: 0pt,
        [#text(size: 11.5pt, fill: ink)[`http`、`www`、可疑域名]],
      ),
      showybox(
        title: text(size: 15pt, weight: "bold", fill: sysu-red)[联系方式],
        frame: (
          title-color: pale-red,
          body-color: pale-red,
          border-color: sysu-red,
          radius: 7pt,
          thickness: 1pt,
          title-inset: (left: 10pt, right: 10pt, top: 7pt, bottom: 8pt),
          body-inset: (left: 10pt, right: 10pt, top: 1pt, bottom: 8pt),
        ),
        title-style: (sep-thickness: 0pt),
        spacing: 0pt,
        [#text(size: 11.5pt, fill: ink)[手机号、微信、`vx` / `wx`]],
      ),
      showybox(
        title: text(size: 15pt, weight: "bold", fill: rgb("#a36a00"))[利益诱导],
        frame: (
          title-color: pale-gold,
          body-color: pale-gold,
          border-color: rgb("#a36a00"),
          radius: 7pt,
          thickness: 1pt,
          title-inset: (left: 10pt, right: 10pt, top: 7pt, bottom: 8pt),
          body-inset: (left: 10pt, right: 10pt, top: 1pt, bottom: 8pt),
        ),
        title-style: (sep-thickness: 0pt),
        spacing: 0pt,
        [#text(size: 11.5pt, fill: ink)[返现、红包、优惠、佣金]],
      ),
      showybox(
        title: text(size: 15pt, weight: "bold", fill: sysu-red)[高风险词],
        frame: (
          title-color: pale-red,
          body-color: pale-red,
          border-color: sysu-red,
          radius: 7pt,
          thickness: 1pt,
          title-inset: (left: 10pt, right: 10pt, top: 7pt, bottom: 8pt),
          body-inset: (left: 10pt, right: 10pt, top: 1pt, bottom: 8pt),
        ),
        title-style: (sep-thickness: 0pt),
        spacing: 0pt,
        [#text(size: 11.5pt, fill: ink)[刷单、博彩、贷款、套现]],
      ),
    )
  ],
  [
    #text(size: 16pt, weight: "bold", fill: sysu-red)[字符变体归一化]
    #v(8pt)
    #block(
      width: 100%,
      fill: rgb("#f6f8f7"),
      stroke: 0.8pt + line,
      radius: 8pt,
      inset: 14pt,
      [
        #align(center)[
          #diagram(
            spacing: (10mm, 4mm),
            edge-stroke: 1.1pt + sysu-green,
            node((0, 0), text(size: 10pt)[薇 / 徽 / v], width: 30mm, height: 11mm, fill: white, stroke: 0.8pt + line, corner-radius: 5pt),
            edge((0, 0), (1, 0), "->"),
            node((1, 0), text(size: 11pt, weight: "bold", fill: sysu-green)[微], width: 24mm, height: 11mm, fill: pale-green, stroke: 1pt + sysu-green, corner-radius: 5pt),
            node((0, 1), text(size: 10pt)[辛 / 芯 / 心], width: 30mm, height: 11mm, fill: white, stroke: 0.8pt + line, corner-radius: 5pt),
            edge((0, 1), (1, 1), "->"),
            node((1, 1), text(size: 11pt, weight: "bold", fill: sysu-green)[信], width: 24mm, height: 11mm, fill: pale-green, stroke: 1pt + sysu-green, corner-radius: 5pt),
            node((0, 2), text(size: 10pt)[wx / vx / v信], width: 30mm, height: 11mm, fill: white, stroke: 0.8pt + line, corner-radius: 5pt),
            edge((0, 2), (1, 2), "->"),
            node((1, 2), text(size: 11pt, weight: "bold", fill: sysu-green)[微信], width: 24mm, height: 11mm, fill: pale-green, stroke: 1pt + sysu-green, corner-radius: 5pt),
          )
        ]
      ],
    )
    #v(10pt)
    #showybox(
      title: text(size: 17pt, weight: "bold", fill: sysu-green)[处理效果],
      frame: (
        title-color: pale-green,
        body-color: pale-green,
        border-color: sysu-green,
        radius: 7pt,
        thickness: 1pt,
        title-inset: (left: 12pt, right: 12pt, top: 8pt, bottom: 8pt),
        body-inset: (left: 12pt, right: 12pt, top: 2pt, bottom: 10pt),
      ),
      title-style: (sep-thickness: 0pt),
      spacing: 0pt,
      [
        #text(size: 12.5pt, fill: ink)[
          `加 薇 信 领·取 优 惠`
          #linebreak()
          #text(fill: sysu-green, weight: "bold")[→ 加微信领取优惠]
        ]
      ],
    )
  ],
)

== TF-IDF/LR：传统机器学习基线

#grid(
  columns: (1.12fr, 0.88fr),
  column-gutter: 18pt,
  [
    #text(size: 17pt, weight: "bold", fill: sysu-green)[轻量、快速、可复现]
    #v(11pt)
    #align(center)[
      #diagram(
        spacing: (7mm, 0mm),
        edge-stroke: 1.1pt + sysu-green,
        node(
          (0, 0),
          align(center)[
            #text(size: 11pt, weight: "bold", fill: sysu-green)[字符切分]
            #linebreak()
            #text(size: 7.5pt, fill: muted)[原文 + 归一化文本]
          ],
          width: 30mm,
          height: 15mm,
          fill: pale-green,
          stroke: 1pt + sysu-green,
          corner-radius: 6pt,
        ),
        edge((0, 0), (1, 0), "->"),
        node(
          (1, 0),
          align(center)[
            #text(size: 11pt, weight: "bold", fill: sysu-red)[TF-IDF]
            #linebreak()
            #text(size: 7.5pt, fill: muted)[字符 1–4 gram]
          ],
          width: 28mm,
          height: 15mm,
          fill: pale-red,
          stroke: 1pt + sysu-red,
          corner-radius: 6pt,
        ),
        edge((1, 0), (2, 0), "->"),
        node(
          (2, 0),
          align(center)[
            #text(size: 9pt, weight: "bold", fill: sysu-green)[Logistic Regression]
            #linebreak()
            #text(size: 7pt, fill: muted)[输出垃圾概率]
          ],
          width: 36mm,
          height: 18mm,
          fill: pale-green,
          stroke: 1pt + sysu-green,
          corner-radius: 6pt,
        ),
      )
    ]
    #v(17pt)
    #block(
      fill: pale-green,
      stroke: 1pt + sysu-green.lighten(55%),
      radius: 8pt,
      inset: 13pt,
      [
        #text(size: 13.5pt, fill: ink)[
          通过字符级 n-gram 捕捉“加微信”“返现”“扫码”等局部组合，无需中文分词，训练与推理成本低。
        ]
      ],
    )
  ],
  [
    #showybox(
      frame: (
        body-color: sysu-green.lighten(88%),
        border-color: sysu-green.lighten(55%),
        radius: 8pt,
        thickness: 1pt,
        body-inset: 12pt,
      ),
      spacing: 0pt,
      [
        #align(center)[
          #text(size: 27pt, weight: "bold", fill: sysu-green)[1–4]
          #v(2pt)
          #text(size: 11.5pt, fill: ink)[字符 n-gram 范围]
        ]
      ],
    )
    #v(10pt)
    #showybox(
      frame: (
        body-color: sysu-red.lighten(88%),
        border-color: sysu-red.lighten(55%),
        radius: 8pt,
        thickness: 1pt,
        body-inset: 12pt,
      ),
      spacing: 0pt,
      [
        #align(center)[
          #text(size: 27pt, weight: "bold", fill: sysu-red)[Balanced]
          #v(2pt)
          #text(size: 11.5pt, fill: ink)[类别权重设置]
        ]
      ],
    )
    #v(10pt)
    #showybox(
      frame: (
        body-color: rgb("#a36a00").lighten(88%),
        border-color: rgb("#a36a00").lighten(55%),
        radius: 8pt,
        thickness: 1pt,
        body-inset: 12pt,
      ),
      spacing: 0pt,
      [
        #align(center)[
          #text(size: 27pt, weight: "bold", fill: rgb("#a36a00"))[Baseline]
          #v(2pt)
          #text(size: 11.5pt, fill: ink)[传统方法定位]
        ]
      ],
    )
  ],
)

== 百万级多语言 RoBERTa

#grid(
  columns: (0.92fr, 1.08fr),
  column-gutter: 18pt,
  [
    #grid(
      columns: (1fr, 1fr),
      column-gutter: 10pt,
      row-gutter: 10pt,
      showybox(
        frame: (
          body-color: sysu-green.lighten(88%),
          border-color: sysu-green.lighten(55%),
          radius: 8pt,
          thickness: 1pt,
          body-inset: 12pt,
        ),
        spacing: 0pt,
        [
          #align(center)[
            #text(size: 27pt, weight: "bold", fill: sysu-green)[百万级]
            #v(2pt)
            #text(size: 11.5pt, fill: ink)[去重后的多源训练数据]
          ]
        ],
      ),
      showybox(
        frame: (
          body-color: sysu-red.lighten(88%),
          border-color: sysu-red.lighten(55%),
          radius: 8pt,
          thickness: 1pt,
          body-inset: 12pt,
        ),
        spacing: 0pt,
        [
          #align(center)[
            #text(size: 27pt, weight: "bold", fill: sysu-red)[多语言]
            #v(2pt)
            #text(size: 11.5pt, fill: ink)[中文、英文等文本]
          ]
        ],
      ),
      showybox(
        frame: (
          body-color: sysu-red.lighten(88%),
          border-color: sysu-red.lighten(55%),
          radius: 8pt,
          thickness: 1pt,
          body-inset: 12pt,
        ),
        spacing: 0pt,
        [
          #align(center)[
            #text(size: 27pt, weight: "bold", fill: sysu-red)[4 × H100]
            #v(2pt)
            #text(size: 11.5pt, fill: ink)[并行训练设备]
          ]
        ],
      ),
      showybox(
        frame: (
          body-color: sysu-green.lighten(88%),
          border-color: sysu-green.lighten(55%),
          radius: 8pt,
          thickness: 1pt,
          body-inset: 12pt,
        ),
        spacing: 0pt,
        [
          #align(center)[
            #text(size: 27pt, weight: "bold", fill: sysu-green)[≈ 2 小时]
            #v(2pt)
            #text(size: 11.5pt, fill: ink)[完整训练耗时]
          ]
        ],
      ),
    )
  ],
  [
    #text(size: 17pt, weight: "bold", fill: sysu-red)[项目的主要语义模型]
    #v(9pt)
    #showybox(
      title: text(size: 17pt, weight: "bold", fill: sysu-red)[上下文建模],
      frame: (
        title-color: pale-red,
        body-color: pale-red,
        border-color: sysu-red,
        radius: 7pt,
        thickness: 1pt,
        title-inset: (left: 12pt, right: 12pt, top: 8pt, bottom: 8pt),
        body-inset: (left: 12pt, right: 12pt, top: 2pt, bottom: 10pt),
      ),
      title-style: (sep-thickness: 0pt),
      spacing: 0pt,
      [#text(size: 12.5pt, fill: ink)[基于 XLM-RoBERTa 编码整段文本语义，减少仅凭单个关键词造成的误判。]],
    )
    #v(8pt)
    #showybox(
      title: text(size: 17pt, weight: "bold", fill: sysu-green)[跨语言泛化],
      frame: (
        title-color: pale-green,
        body-color: pale-green,
        border-color: sysu-green,
        radius: 7pt,
        thickness: 1pt,
        title-inset: (left: 12pt, right: 12pt, top: 8pt, bottom: 8pt),
        body-inset: (left: 12pt, right: 12pt, top: 2pt, bottom: 10pt),
      ),
      title-style: (sep-thickness: 0pt),
      spacing: 0pt,
      [#text(size: 12.5pt, fill: ink)[统一模型处理多语言输入，为英文短信和混合语言广告提供检测能力；训练过程以 F1 选择最佳模型。]],
    )
  ],
)

== 多模块融合架构

#align(center)[
  #diagram(
    spacing: (5mm, 4mm),
    edge-stroke: 1pt + sysu-green,
    node(
      (1.5, 0),
      align(center)[
        #text(size: 12pt, weight: "bold", fill: sysu-green)[输入文本]
        #linebreak()
        #text(size: 8pt, fill: muted)[中文 / 英文 / 混合语言]
      ],
      name: <input>,
      width: 38mm,
      height: 15mm,
      fill: pale-green,
      stroke: 1.1pt + sysu-green,
      corner-radius: 7pt,
    ),
    node((0, 1), align(center)[#text(size: 10.5pt, weight: "bold", fill: sysu-green)[规则分数] #linebreak() #text(size: 7pt, fill: muted)[链接、号码、风险词]], name: <rule>, width: 30mm, height: 14mm, fill: white, stroke: 1pt + sysu-green, corner-radius: 6pt),
    node((1, 1), align(center)[#text(size: 10.5pt, weight: "bold", fill: sysu-red)[变体分数] #linebreak() #text(size: 7pt, fill: muted)[形近字、缩写、分隔符]], name: <variant>, width: 30mm, height: 14mm, fill: pale-red, stroke: 1pt + sysu-red, corner-radius: 6pt),
    node((2, 1), align(center)[#text(size: 10.5pt, weight: "bold", fill: sysu-green)[TF-IDF/LR] #linebreak() #text(size: 7pt, fill: muted)[传统统计分类]], name: <tfidf>, width: 30mm, height: 14mm, fill: white, stroke: 1pt + sysu-green, corner-radius: 6pt),
    node((3, 1), align(center)[#text(size: 10.5pt, weight: "bold", fill: sysu-red)[RoBERTa] #linebreak() #text(size: 7pt, fill: muted)[多语言语义分类]], name: <roberta>, width: 30mm, height: 14mm, fill: pale-red, stroke: 1pt + sysu-red, corner-radius: 6pt),
    node(
      (1.5, 2),
      align(center)[
        #text(size: 12pt, weight: "bold", fill: sysu-red)[融合评分]
        #linebreak()
        #text(size: 8pt, fill: muted)[风险分数 0–1]
      ],
      name: <fusion>,
      width: 38mm,
      height: 15mm,
      fill: pale-red,
      stroke: 1.1pt + sysu-red,
      corner-radius: 7pt,
    ),
    node(
      (1.5, 3),
      align(center)[
        #text(size: 12pt, weight: "bold", fill: sysu-green)[最终输出]
        #linebreak()
        #text(size: 8pt, fill: muted)[类别 + 原因 + 模块分数]
      ],
      name: <output>,
      width: 42mm,
      height: 15mm,
      fill: pale-green,
      stroke: 1.1pt + sysu-green,
      corner-radius: 7pt,
    ),
    edge(<input>, <rule>, "-"),
    edge(<input>, <variant>, "-"),
    edge(<input>, <tfidf>, "-"),
    edge(<input>, <roberta>, "-"),
    edge(<rule>, <fusion>, "-"),
    edge(<variant>, <fusion>, "-"),
    edge(<tfidf>, <fusion>, "-"),
    edge(<roberta>, <fusion>, "-"),
    edge(<fusion>, <output>, "-"),
  )
]

#v(6pt)

#align(center)[
  #block(
    fill: ink,
    radius: 8pt,
    inset: 13pt,
    align(center)[
      #text(size: 15pt, fill: white)[
        $ "score" = 0.20 dot "rule" + 0.70 dot "model" + 0.10 dot "variant" $
      ]
    ],
  )
]
#v(9pt)
#align(center)[
  #text(size: 12pt, fill: muted)[模型模式可在 TF-IDF/LR、RoBERTa、双模型与纯规则之间切换]
]

= 实验结果与分析

== 实验设置与评价指标

#grid(
  columns: (1fr, 1.05fr),
  column-gutter: 18pt,
  [
    #text(size: 16pt, weight: "bold", fill: sysu-green)[实验流程]
    #v(9pt)
    #align(center)[
      #diagram(
        spacing: (7mm, 6mm),
        edge-stroke: 1.1pt + sysu-green,
        node((0, 0), align(center)[#text(size: 11pt, weight: "bold", fill: sysu-green)[训练集] #linebreak() #text(size: 7.5pt, fill: muted)[模型参数学习]], width: 31mm, height: 15mm, fill: pale-green, stroke: 1pt + sysu-green, corner-radius: 6pt),
        edge((0, 0), (1, 0), "->"),
        node((1, 0), align(center)[#text(size: 11pt, weight: "bold", fill: sysu-red)[验证集] #linebreak() #text(size: 7.5pt, fill: muted)[模型选择与调参]], width: 31mm, height: 15mm, fill: pale-red, stroke: 1pt + sysu-red, corner-radius: 6pt),
        edge((1, 0), (1, 1), "->"),
        node((1, 1), align(center)[#text(size: 11pt, weight: "bold", fill: sysu-red)[系统测试] #linebreak() #text(size: 7.5pt, fill: muted)[单条与批量推理]], width: 31mm, height: 15mm, fill: pale-red, stroke: 1pt + sysu-red, corner-radius: 6pt),
        edge((1, 1), (0, 1), "->"),
        node((0, 1), align(center)[#text(size: 11pt, weight: "bold", fill: sysu-green)[困难样例] #linebreak() #text(size: 7.5pt, fill: muted)[变体与误报测试]], width: 31mm, height: 15mm, fill: pale-green, stroke: 1pt + sysu-green, corner-radius: 6pt),
      )
    ]
  ],
  [
    #text(size: 16pt, weight: "bold", fill: sysu-red)[四项核心指标]
    #v(9pt)
    #grid(
      columns: (1fr, 1fr),
      column-gutter: 9pt,
      row-gutter: 9pt,
      showybox(
        frame: (
          body-color: sysu-green.lighten(88%),
          border-color: sysu-green.lighten(55%),
          radius: 8pt,
          thickness: 1pt,
          body-inset: 12pt,
        ),
        spacing: 0pt,
        [
          #align(center)[
            #text(size: 27pt, weight: "bold", fill: sysu-green)[Accuracy]
            #v(2pt)
            #text(size: 11.5pt, fill: ink)[整体分类正确率]
          ]
        ],
      ),
      showybox(
        frame: (
          body-color: sysu-red.lighten(88%),
          border-color: sysu-red.lighten(55%),
          radius: 8pt,
          thickness: 1pt,
          body-inset: 12pt,
        ),
        spacing: 0pt,
        [
          #align(center)[
            #text(size: 27pt, weight: "bold", fill: sysu-red)[Precision]
            #v(2pt)
            #text(size: 11.5pt, fill: ink)[垃圾判定的准确程度]
          ]
        ],
      ),
      showybox(
        frame: (
          body-color: rgb("#a36a00").lighten(88%),
          border-color: rgb("#a36a00").lighten(55%),
          radius: 8pt,
          thickness: 1pt,
          body-inset: 12pt,
        ),
        spacing: 0pt,
        [
          #align(center)[
            #text(size: 27pt, weight: "bold", fill: rgb("#a36a00"))[Recall]
            #v(2pt)
            #text(size: 11.5pt, fill: ink)[实际垃圾文本检出率]
          ]
        ],
      ),
      showybox(
        frame: (
          body-color: sysu-green.lighten(88%),
          border-color: sysu-green.lighten(55%),
          radius: 8pt,
          thickness: 1pt,
          body-inset: 12pt,
        ),
        spacing: 0pt,
        [
          #align(center)[
            #text(size: 27pt, weight: "bold", fill: sysu-green)[F1]
            #v(2pt)
            #text(size: 11.5pt, fill: ink)[Precision 与 Recall 的平衡]
          ]
        ],
      ),
    )
  ],
)

#v(13pt)
#align(center)[
  #text(size: 13pt, weight: "bold", fill: ink)[
    垃圾检测更关注 Precision 与 Recall 的平衡，因此训练过程以 F1 选择最佳模型。
  ]
]

== 不同检测方法结果对比

#grid(
  columns: (1.35fr, 0.65fr),
  column-gutter: 16pt,
  [
    #image("../figures/model_comparison.png", width: 100%)
  ],
  [
    #showybox(
      title: text(size: 17pt, weight: "bold", fill: rgb("#a36a00"))[规则模型],
      frame: (
        title-color: pale-gold,
        body-color: pale-gold,
        border-color: rgb("#a36a00"),
        radius: 7pt,
        thickness: 1pt,
        title-inset: (left: 12pt, right: 12pt, top: 8pt, bottom: 8pt),
        body-inset: (left: 12pt, right: 12pt, top: 2pt, bottom: 10pt),
      ),
      title-style: (sep-thickness: 0pt),
      spacing: 0pt,
      [#text(size: 12.5pt, fill: ink)[可解释性强，能够快速定位链接、联系方式和高风险词。]],
    )
    #v(8pt)
    #showybox(
      title: text(size: 17pt, weight: "bold", fill: sysu-green)[传统基线],
      frame: (
        title-color: pale-green,
        body-color: pale-green,
        border-color: sysu-green,
        radius: 7pt,
        thickness: 1pt,
        title-inset: (left: 12pt, right: 12pt, top: 8pt, bottom: 8pt),
        body-inset: (left: 12pt, right: 12pt, top: 2pt, bottom: 10pt),
      ),
      title-style: (sep-thickness: 0pt),
      spacing: 0pt,
      [#text(size: 12.5pt, fill: ink)[字符级 TF-IDF/LR 在当前评测集上提供稳定、低成本的分类能力。]],
    )
    #v(8pt)
    #showybox(
      title: text(size: 17pt, weight: "bold", fill: sysu-red)[融合检测],
      frame: (
        title-color: pale-red,
        body-color: pale-red,
        border-color: sysu-red,
        radius: 7pt,
        thickness: 1pt,
        title-inset: (left: 12pt, right: 12pt, top: 8pt, bottom: 8pt),
        body-inset: (left: 12pt, right: 12pt, top: 2pt, bottom: 10pt),
      ),
      title-style: (sep-thickness: 0pt),
      spacing: 0pt,
      [#text(size: 12.5pt, fill: ink)[结合规则、变体与模型概率，兼顾结果性能和可解释性。]],
    )
  ],
)

== 多语言与变体案例分析

#grid(
  columns: (1fr, 1fr),
  column-gutter: 14pt,
  row-gutter: 12pt,
  showybox(
    title: text(size: 17pt, weight: "bold", fill: sysu-red)[中文变体广告],
    frame: (
      title-color: pale-red,
      body-color: pale-red,
      border-color: sysu-red,
      radius: 7pt,
      thickness: 1pt,
      title-inset: (left: 12pt, right: 12pt, top: 8pt, bottom: 8pt),
      body-inset: (left: 12pt, right: 12pt, top: 2pt, bottom: 10pt),
    ),
    title-style: (sep-thickness: 0pt),
    spacing: 0pt,
    [
      #text(size: 12.5pt, fill: ink)[
        `加 薇 信 免费领·取资料`
        #v(5pt)
        #text(fill: sysu-red, weight: "bold")[识别：形近字 + 分隔符 + 引流意图]
      ]
    ],
  ),
  showybox(
    title: text(size: 17pt, weight: "bold", fill: sysu-red)[英文垃圾短信],
    frame: (
      title-color: pale-red,
      body-color: pale-red,
      border-color: sysu-red,
      radius: 7pt,
      thickness: 1pt,
      title-inset: (left: 12pt, right: 12pt, top: 8pt, bottom: 8pt),
      body-inset: (left: 12pt, right: 12pt, top: 2pt, bottom: 10pt),
    ),
    title-style: (sep-thickness: 0pt),
    spacing: 0pt,
    [
      #text(size: 12.5pt, fill: ink)[
        `Claim your free prize now!`
        #v(5pt)
        #text(fill: sysu-red, weight: "bold")[识别：RoBERTa 跨语言语义分类]
      ]
    ],
  ),
  showybox(
    title: text(size: 17pt, weight: "bold", fill: sysu-green)[正常技术文本],
    frame: (
      title-color: pale-green,
      body-color: pale-green,
      border-color: sysu-green,
      radius: 7pt,
      thickness: 1pt,
      title-inset: (left: 12pt, right: 12pt, top: 8pt, bottom: 8pt),
      body-inset: (left: 12pt, right: 12pt, top: 2pt, bottom: 10pt),
    ),
    title-style: (sep-thickness: 0pt),
    spacing: 0pt,
    [
      #text(size: 12.5pt, fill: ink)[
        `微信小程序开发需要配置环境`
        #v(5pt)
        #text(fill: sysu-green, weight: "bold")[判定：结合上下文，降低关键词误报]
      ]
    ],
  ),
  showybox(
    title: text(size: 17pt, weight: "bold", fill: rgb("#a36a00"))[混合语言广告],
    frame: (
      title-color: pale-gold,
      body-color: pale-gold,
      border-color: rgb("#a36a00"),
      radius: 7pt,
      thickness: 1pt,
      title-inset: (left: 12pt, right: 12pt, top: 8pt, bottom: 8pt),
      body-inset: (left: 12pt, right: 12pt, top: 2pt, bottom: 10pt),
    ),
    title-style: (sep-thickness: 0pt),
    spacing: 0pt,
    [
      #text(size: 12.5pt, fill: ink)[
        `Add vx for 优惠 and bonus`
        #v(5pt)
        #text(fill: sysu-red, weight: "bold")[识别：缩写规则 + 多语言模型]
      ]
    ],
  ),
)

#v(11pt)
#align(center)[
  #text(size: 14pt, weight: "bold", fill: ink)[
    规则负责“看见风险信号”，RoBERTa 负责“理解上下文意图”。
  ]
]

= 系统展示与总结

== 系统演示与项目总结

#grid(
  columns: (1.08fr, 0.92fr),
  column-gutter: 18pt,
  [
    #block(
      width: 100%,
      height: 178pt,
      fill: gradient.linear(sysu-green, ink, angle: 135deg),
      radius: 12pt,
      inset: 18pt,
      align(center + horizon)[
        #text(size: 30pt, weight: "bold", fill: white)[▶ DEMO]
        #v(8pt)
        #text(size: 15pt, fill: white)[播放系统录屏]
      ],
    )
  ],
  [
    #text(size: 16pt, weight: "bold", fill: sysu-green)[已完成的系统能力]
    #v(6pt)
    #block(
      fill: rgb("#f6f8f7"),
      stroke: 0.8pt + line,
      radius: 8pt,
      inset: 11pt,
      [
        #text(size: 12.5pt, weight: "bold", fill: sysu-green)[检测模式]
        #h(8pt)
        #text(size: 11.5pt, fill: ink)[TF-IDF/LR、RoBERTa、双模型、规则变体]
        #v(8pt)
        #text(size: 12.5pt, weight: "bold", fill: sysu-red)[交互功能]
        #h(8pt)
        #text(size: 11.5pt, fill: ink)[单条检测、批量上传、结果下载、模块对比]
        #v(8pt)
        #text(size: 12.5pt, weight: "bold", fill: rgb("#a36a00"))[解释输出]
        #h(8pt)
        #text(size: 11.5pt, fill: ink)[风险分数、关键词高亮、归一化与命中原因]
      ],
    )
  ],
)

#v(9pt)
#grid(
  columns: (1fr, 1fr, 1fr, 1fr),
  column-gutter: 8pt,
  block(fill: pale-green, radius: 5pt, inset: 7pt, align(center)[#text(size: 10.5pt, weight: "bold", fill: sysu-green)[数据与标注]]),
  block(fill: pale-green, radius: 5pt, inset: 7pt, align(center)[#text(size: 10.5pt, weight: "bold", fill: sysu-green)[规则与基线]]),
  block(fill: pale-green, radius: 5pt, inset: 7pt, align(center)[#text(size: 10.5pt, weight: "bold", fill: sysu-green)[RoBERTa 训练]]),
  block(fill: pale-green, radius: 5pt, inset: 7pt, align(center)[#text(size: 10.5pt, weight: "bold", fill: sysu-green)[系统与展示]]),
)

#ending-slide(
  title: [感谢聆听],
  [
    #text(size: 25pt, weight: "bold", fill: sysu-green)[Q & A]
    #v(10pt)
    #text(size: 14pt, fill: ink)[基于字符相似性与机器学习的互联网垃圾文本检测系统]
  ],
)
