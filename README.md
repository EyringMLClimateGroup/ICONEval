> [!IMPORTANT]
> Currently (March 2026), this repository contains an early version of
> ICONEval, which is targeted to the evaluation of
> [ICON](https://www.icon-model.org/) output on [DKRZ's
> Levante](https://docs.dkrz.de/doc/levante/).

---

[![LICENSE](https://img.shields.io/badge/License-Apache%202.0-blue)](https://www.apache.org/licenses/LICENSE-2.0.html)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18937450.svg)](https://doi.org/10.5281/zenodo.18937450)
[![SPEC 0 — Minimum Supported Dependencies](https://img.shields.io/badge/SPEC-0-green?labelColor=%23004811&color=%235CA038)](https://scientific-python.org/specs/spec-0000/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/EyringMLClimateGroup/ICONEval/main.svg)](https://results.pre-commit.ci/latest/github/EyringMLClimateGroup/ICONEval/main)
[![Run tests](https://github.com/EyringMLClimateGroup/ICONEval/actions/workflows/run_tests.yml/badge.svg)](https://github.com/EyringMLClimateGroup/ICONEval/actions/workflows/run_tests.yml)
<!-- Pytest Coverage Comment:Begin -->
<a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/README.md"><img alt="Coverage" src="https://img.shields.io/badge/Coverage-74%25-yellow.svg" /></a><details><summary>Coverage Report </summary><table><tr><th>File</th><th>Stmts</th><th>Miss</th><th>Cover</th><th>Missing</th></tr><tbody><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/__init__.py">__init__.py</a></td><td>16</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/_config.py">_config.py</a></td><td>11</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/_dependencies.py">_dependencies.py</a></td><td>20</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/_io_handler.py">_io_handler.py</a></td><td>185</td><td>3</td><td>98%</td><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/_io_handler.py#L273-L274">273&ndash;274</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/_io_handler.py#L299">299</a></td></tr><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/_job.py">_job.py</a></td><td>98</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/_logging.py">_logging.py</a></td><td>12</td><td>3</td><td>75%</td><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/_logging.py#L27-L29">27&ndash;29</a></td></tr><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/_recipe.py">_recipe.py</a></td><td>10</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/_simulation_info.py">_simulation_info.py</a></td><td>42</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/_templates.py">_templates.py</a></td><td>220</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/_typing.py">_typing.py</a></td><td>6</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/main.py">main.py</a></td><td>172</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td colspan="5"><b>output_handling</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/__init__.py">__init__.py</a></td><td>0</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py">_summarize.py</a></td><td>193</td><td>109</td><td>43%</td><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L129">129</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L138-L145">138&ndash;145</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L149">149</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L156-L157">156&ndash;157</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L160-L161">160&ndash;161</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L163-L166">163&ndash;166</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L194">194</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L214-L217">214&ndash;217</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L219-L223">219&ndash;223</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L225-L229">225&ndash;229</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L231-L232">231&ndash;232</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L239-L244">239&ndash;244</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L263-L268">263&ndash;268</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L275-L280">275&ndash;280</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L285">285</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L287-L290">287&ndash;290</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L292-L295">292&ndash;295</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L297">297</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L302-L304">302&ndash;304</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L306-L308">306&ndash;308</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L310-L317">310&ndash;317</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L319-L321">319&ndash;321</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L323-L325">323&ndash;325</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L330-L331">330&ndash;331</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L333-L334">333&ndash;334</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L336">336</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L341">341</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L346-L347">346&ndash;347</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L349-L350">349&ndash;350</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L352-L354">352&ndash;354</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L356-L358">356&ndash;358</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L360-L364">360&ndash;364</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L366">366</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L371">371</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L443">443</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/_summarize.py#L522-L523">522&ndash;523</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py">plots2pdf.py</a></td><td>184</td><td>156</td><td>15%</td><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L105-L106">105&ndash;106</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L109-L110">109&ndash;110</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L114-L124">114&ndash;124</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L128-L129">128&ndash;129</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L132-L134">132&ndash;134</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L138-L139">138&ndash;139</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L144-L149">144&ndash;149</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L153-L154">153&ndash;154</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L157-L158">157&ndash;158</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L161">161</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L164-L169">164&ndash;169</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L171">171</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L206">206</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L209-L210">209&ndash;210</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L212">212</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L248-L249">248&ndash;249</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L252-L254">252&ndash;254</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L259">259</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L261-L264">261&ndash;264</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L266-L268">266&ndash;268</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L271">271</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L278-L279">278&ndash;279</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L283">283</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L286-L289">286&ndash;289</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L296-L300">296&ndash;300</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L302-L304">302&ndash;304</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L306">306</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L309-L310">309&ndash;310</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L314">314</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L318-L319">318&ndash;319</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L321">321</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L325">325</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L330">330</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L334-L337">334&ndash;337</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L343-L344">343&ndash;344</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L347-L348">347&ndash;348</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L351-L352">351&ndash;352</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L356">356</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L379">379</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L382-L384">382&ndash;384</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L386-L388">386&ndash;388</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L391-L394">391&ndash;394</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L396">396</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L401-L403">401&ndash;403</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L408-L410">408&ndash;410</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L427-L430">427&ndash;430</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L434-L439">434&ndash;439</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L444">444</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L447-L448">447&ndash;448</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L452-L458">452&ndash;458</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L461">461</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L470-L480">470&ndash;480</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L484-L487">484&ndash;487</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L491-L494">491&ndash;494</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L498-L500">498&ndash;500</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/plots2pdf.py#L505-L506">505&ndash;506</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/publish_html.py">publish_html.py</a></td><td>115</td><td>58</td><td>49%</td><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/publish_html.py#L94">94</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/publish_html.py#L98-L99">98&ndash;99</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/publish_html.py#L109">109</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/publish_html.py#L130-L133">130&ndash;133</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/publish_html.py#L135-L138">135&ndash;138</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/publish_html.py#L140-L141">140&ndash;141</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/publish_html.py#L149">149</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/publish_html.py#L151-L155">151&ndash;155</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/publish_html.py#L157-L158">157&ndash;158</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/publish_html.py#L166">166</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/publish_html.py#L168-L172">168&ndash;172</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/publish_html.py#L174">174</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/publish_html.py#L194">194</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/publish_html.py#L196">196</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/publish_html.py#L215">215</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/publish_html.py#L229-L231">229&ndash;231</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/publish_html.py#L249-L250">249&ndash;250</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/publish_html.py#L252-L253">252&ndash;253</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/publish_html.py#L255-L256">255&ndash;256</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/publish_html.py#L258">258</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/publish_html.py#L263-L265">263&ndash;265</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/publish_html.py#L267">267</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/publish_html.py#L270-L273">270&ndash;273</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/publish_html.py#L276-L280">276&ndash;280</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/publish_html.py#L282">282</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/iconeval/output_handling/publish_html.py#L287-L288">287&ndash;288</a></td></tr><tr><td><b>TOTAL</b></td><td><b>1284</b></td><td><b>329</b></td><td><b>74%</b></td><td>&nbsp;</td></tr></tbody></table></details>
<!-- Pytest Coverage Comment:End -->

---

# ICONEval

ICON model output evaluation with ESMValTool.

## Table of Contents

1. [Quick Start](#quick-start)
1. [Prerequisites](#prerequisites)
1. [Installation](#installation)
1. [Customization](#customization)
1. [Common ICON Output Format](#common-icon-output-format)
1. [FAQs](#faqs)

## Quick Start

ICONEval facilitates the evaluation of [ICON
model](https://www.icon-model.org/) output with [ESMValTool](doc/esmvaltool.md)
by automatically running a set of predefined ESMValTool recipes. Its only
necessary input is a valid path to ICON model output:

```bash
iconeval path/to/ICON_output
```

This path should point to the directory whose name is identical to the
experiment name of the ICON simulation you want to evaluate, e.g.,
`/root/to/my_amip_run` for the experiment `my_amip_run`. In this case, for
example, the simulation output files should be named
`my_amip_run_atm_2d_ml_<date>.nc` or `my_amip_run_lnd_mon_<date>.nc`. Multiple
simulations can be evaluated simultaneously by specifying multiple directories:

```bash
iconeval path/to/ICON_output path/to/other/ICON_output
```

ICONEval reads a set of file templates (ESMValTool recipes and ESMValTool
configuration) and fills these with the information from the ICON simulation
that will be evaluated. If no further options are specified, a set of default
recipes with default settings are run. If ICONEval is run as a standalone
script, one [Slurm](https://slurm.schedmd.com/) job per recipe is launched. If
ICONEval is run within an `sbatch` script or `salloc` session, one job step per
recipe is created. The following `sbatch` script can be used to submit a job on
a compute node of [DKRZ's Levante](https://docs.dkrz.de/doc/levante/) in which
8 recipes are run in parallel (see
[here](doc/customization.md#slurm-options-for-jobjob-step-submission) for
details on this):

```bash
#!/bin/bash -e
#SBATCH --mem=0
#SBATCH --nodes=1
#SBATCH --partition=compute
#SBATCH --time=03:00:00

iconeval path/to/ICON_output --srun_options='{"--cpus-per-task": 16, "--mem-per-cpu": "1940M"}'
```

ICONEval is highly customizable. For example, the desired time range and
frequency of the input data, as well as a flag to publish a summary HTML on a
**public** website can be passed with

```bash
iconeval path/to/ICON_output --timerange='20070101/20080101' --frequency=mon --publish_html=True
```

Publishing results via the command line option `--publish_html=True` uses the
[Swift object storage of
DKRZ](https://docs.dkrz.de/doc/datastorage/swift/python-swiftclient.html) and
requires a DKRZ account. User authentication works via a *Swift token* that
needs to be renewed monthly. If the token needs to be renewed, the user is
prompted for their DKRZ account and password information when running ICONEval.
The token can also be regenerated manually, see [FAQs](doc/faqs.md) for
details. The raw files (figures and data) from published results can be
accessed via DKRZ's [Swiftbrowser](https://swiftbrowser.dkrz.de/).

To only run a subset of available recipes, you can specify `--tags` when
running ICONEval:

```bash
iconeval path/to/ICON_output --tags=timeseries,maps
```

An overview of all tags available in the default recipe templates is given
[here](doc/tags.md).

For more information on this and a list of all options, run

```bash
iconeval -- --help
```

or have a look at the section on [Customization](#customization).

Installing ICONEval also provides the command line tools `plots2pdf` (create
summary PDF for arbitrary ESMValTool output) and `publish_html` (publish
summary HTML on public website for arbitrary ESMValTool output). For more
information on them, run

```bash
plots2pdf -- --help
publish_html -- --help
```

## Example Results

- [Fully coupled historical ICON-XPP
  simulation](https://swift.dkrz.de/v1/dkrz_4eefb34f-8803-415a-bd70-9c455db9a403/iconeval/iconeval_example/index.html)

## Prerequisites

ICONEval needs to run on a machine where the [Slurm Workload
Manager](https://slurm.schedmd.com/) is available for the submission of jobs.

## Installation

On DKRZ's Levante, a pre-installed version of ICONEval is available via a
module. Thus, there is no need to install it yourself as a user on this
machine.

However, on other machines, or if you would like to develop new features for
ICONEval on Levante, an installation from source (*development installation*)
is necessary.

### Levante

To load the ICONEval module on Levante, use

```bash
module use -a /work/bd1179/modulefiles
module load iconeval
```

Add these lines to your shell configuration file if you use ICONEval regularly.
[This file](doc/setup_module.md) describes how the ICONEval module is set up.

### Installation from Source (Development Installation)

Installation from source is described [here](doc/install_from_source.md).

## Customization

ICONEval is highly customizable. Detailed information on this can be found
[here](doc/customization.md).

## Common ICON Output Format

To ensure that ICONEval works smoothly, the ICON simulation output should
follow [these criteria](doc/icon_output_format.md) as closely as possible.

## FAQs

A set of frequently asked questions can be found [here](doc/faqs.md).
