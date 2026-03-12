> [!IMPORTANT]
> Currently (March 2026), this repository contains an early version of
> ICONEval, which is targeted to the evaluation of
> [ICON](https://www.icon-model.org/) output on [DKRZ's
> Levante](https://docs.dkrz.de/doc/levante/).

---

[![LICENSE](https://img.shields.io/badge/License-Apache%202.0-blue)](https://www.apache.org/licenses/LICENSE-2.0.html)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18937450.svg)](https://doi.org/10.5281/zenodo.18937450)
[![SPEC 0 — Minimum Supported Dependencies](https://img.shields.io/badge/SPEC-0-green?labelColor=%23004811&color=%235CA038)](https://scientific-python.org/specs/spec-0000/)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/EyringMLClimateGroup/ICONEval/main.svg)](https://results.pre-commit.ci/latest/github/EyringMLClimateGroup/ICONEval/main)
[![Run tests](https://github.com/EyringMLClimateGroup/ICONEval/actions/workflows/run_tests.yml/badge.svg)](https://github.com/EyringMLClimateGroup/ICONEval/actions/workflows/run_tests.yml)
<!-- Pytest Coverage Comment:Begin -->
<a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/README.md"><img alt="Coverage" src="https://img.shields.io/badge/Coverage-63%25-yellow.svg" /></a><details><summary>Coverage Report </summary><table><tr><th>File</th><th>Stmts</th><th>Miss</th><th>Cover</th><th>Missing</th></tr><tbody><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/__init__.py">__init__.py</a></td><td>16</td><td>5</td><td>68%</td><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/__init__.py#L21-L25">21&ndash;25</a></td></tr><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_config.py">_config.py</a></td><td>11</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_dependencies.py">_dependencies.py</a></td><td>20</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_io_handler.py">_io_handler.py</a></td><td>184</td><td>26</td><td>85%</td><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_io_handler.py#L73">73</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_io_handler.py#L81">81</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_io_handler.py#L221">221</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_io_handler.py#L253">253</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_io_handler.py#L271-L272">271&ndash;272</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_io_handler.py#L279-L280">279&ndash;280</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_io_handler.py#L286">286</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_io_handler.py#L289">289</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_io_handler.py#L297">297</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_io_handler.py#L315">315</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_io_handler.py#L330">330</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_io_handler.py#L332">332</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_io_handler.py#L344-L345">344&ndash;345</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_io_handler.py#L349-L351">349&ndash;351</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_io_handler.py#L353">353</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_io_handler.py#L359-L360">359&ndash;360</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_io_handler.py#L362-L363">362&ndash;363</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_io_handler.py#L380-L381">380&ndash;381</a></td></tr><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_job.py">_job.py</a></td><td>98</td><td>11</td><td>88%</td><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_job.py#L57">57</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_job.py#L94-L98">94&ndash;98</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_job.py#L108">108</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_job.py#L160">160</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_job.py#L173">173</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_job.py#L176">176</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_job.py#L211">211</a></td></tr><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_logging.py">_logging.py</a></td><td>13</td><td>3</td><td>76%</td><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_logging.py#L30-L32">30&ndash;32</a></td></tr><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_recipe.py">_recipe.py</a></td><td>10</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_simulation_info.py">_simulation_info.py</a></td><td>42</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_templates.py">_templates.py</a></td><td>220</td><td>19</td><td>91%</td><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_templates.py#L33">33</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_templates.py#L54">54</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_templates.py#L58">58</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_templates.py#L105-L112">105&ndash;112</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_templates.py#L117">117</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_templates.py#L121">121</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_templates.py#L242">242</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_templates.py#L269">269</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_templates.py#L273">273</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_templates.py#L299">299</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_templates.py#L347">347</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_templates.py#L349">349</a></td></tr><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_typing.py">_typing.py</a></td><td>6</td><td>6</td><td>0%</td><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_typing.py#L3">3</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_typing.py#L5-L6">5&ndash;6</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_typing.py#L8">8</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_typing.py#L11">11</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/_typing.py#L13">13</a></td></tr><tr><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/main.py">main.py</a></td><td>172</td><td>40</td><td>76%</td><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/main.py#L239-L241">239&ndash;241</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/main.py#L254">254</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/main.py#L289-L291">289&ndash;291</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/main.py#L294">294</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/main.py#L302">302</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/main.py#L311">311</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/main.py#L325-L332">325&ndash;332</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/main.py#L334">334</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/main.py#L340-L342">340&ndash;342</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/main.py#L345">345</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/main.py#L359-L362">359&ndash;362</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/main.py#L366">366</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/main.py#L392-L394">392&ndash;394</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/main.py#L398-L399">398&ndash;399</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/main.py#L408">408</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/main.py#L410">410</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/main.py#L435-L436">435&ndash;436</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/main.py#L452-L453">452&ndash;453</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/main.py#L457">457</a></td></tr><tr><td colspan="5"><b>output_handling</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/__init__.py">__init__.py</a></td><td>0</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py">_summarize.py</a></td><td>193</td><td>109</td><td>43%</td><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L128">128</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L137-L144">137&ndash;144</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L148">148</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L155-L156">155&ndash;156</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L159-L160">159&ndash;160</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L162-L165">162&ndash;165</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L193">193</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L213-L216">213&ndash;216</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L218-L222">218&ndash;222</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L224-L228">224&ndash;228</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L230-L231">230&ndash;231</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L238-L243">238&ndash;243</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L262-L267">262&ndash;267</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L274-L279">274&ndash;279</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L284">284</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L286-L289">286&ndash;289</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L291-L294">291&ndash;294</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L296">296</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L301-L303">301&ndash;303</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L305-L307">305&ndash;307</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L309-L316">309&ndash;316</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L318-L320">318&ndash;320</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L322-L324">322&ndash;324</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L329-L330">329&ndash;330</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L332-L333">332&ndash;333</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L335">335</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L340">340</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L345-L346">345&ndash;346</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L348-L349">348&ndash;349</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L351-L353">351&ndash;353</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L355-L357">355&ndash;357</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L359-L363">359&ndash;363</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L365">365</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L370">370</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L442">442</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/_summarize.py#L521-L522">521&ndash;522</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py">plots2pdf.py</a></td><td>185</td><td>156</td><td>15%</td><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L105-L106">105&ndash;106</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L109-L110">109&ndash;110</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L114-L124">114&ndash;124</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L128-L129">128&ndash;129</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L132-L134">132&ndash;134</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L138-L139">138&ndash;139</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L144-L149">144&ndash;149</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L153-L154">153&ndash;154</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L157-L158">157&ndash;158</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L161">161</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L164-L169">164&ndash;169</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L171">171</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L206">206</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L209-L210">209&ndash;210</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L212">212</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L248-L249">248&ndash;249</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L252-L254">252&ndash;254</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L259">259</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L261-L264">261&ndash;264</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L266-L268">266&ndash;268</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L271">271</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L278-L279">278&ndash;279</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L283">283</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L286-L289">286&ndash;289</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L296-L300">296&ndash;300</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L302-L304">302&ndash;304</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L306">306</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L309-L310">309&ndash;310</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L314">314</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L318-L319">318&ndash;319</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L321">321</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L325">325</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L330">330</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L334-L337">334&ndash;337</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L343-L344">343&ndash;344</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L347-L348">347&ndash;348</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L351-L352">351&ndash;352</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L356">356</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L379">379</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L382-L384">382&ndash;384</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L386-L388">386&ndash;388</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L391-L394">391&ndash;394</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L396">396</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L401-L403">401&ndash;403</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L408-L410">408&ndash;410</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L427-L430">427&ndash;430</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L434-L439">434&ndash;439</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L444">444</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L447-L448">447&ndash;448</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L452-L458">452&ndash;458</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L461">461</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L470-L480">470&ndash;480</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L484-L487">484&ndash;487</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L491-L494">491&ndash;494</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L498-L500">498&ndash;500</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L505">505</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/plots2pdf.py#L509">509</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py">publish_html.py</a></td><td>116</td><td>92</td><td>20%</td><td><a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L93-L94">93&ndash;94</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L96-L99">96&ndash;99</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L102-L104">102&ndash;104</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L107-L109">107&ndash;109</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L111">111</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L116">116</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L130-L133">130&ndash;133</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L135-L138">135&ndash;138</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L140-L141">140&ndash;141</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L149">149</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L151-L155">151&ndash;155</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L157-L158">157&ndash;158</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L166">166</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L168-L172">168&ndash;172</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L174">174</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L181-L184">181&ndash;184</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L193-L196">193&ndash;196</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L198-L199">198&ndash;199</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L203-L204">203&ndash;204</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L207">207</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L211-L215">211&ndash;215</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L217-L218">217&ndash;218</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L227-L231">227&ndash;231</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L234">234</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L236">236</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L241-L242">241&ndash;242</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L244">244</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L249-L250">249&ndash;250</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L252-L253">252&ndash;253</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L255-L256">255&ndash;256</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L258">258</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L263-L265">263&ndash;265</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L267">267</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L270-L273">270&ndash;273</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L276-L280">276&ndash;280</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L282">282</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L287">287</a>, <a href="https://github.com/EyringMLClimateGroup/ICONEval/blob/main/output_handling/publish_html.py#L291">291</a></td></tr><tr><td><b>TOTAL</b></td><td><b>1286</b></td><td><b>467</b></td><td><b>63%</b></td><td>&nbsp;</td></tr></tbody></table></details>
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
