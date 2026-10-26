# Citing

If you use SwarmBench in your research, please cite it. The paper has been
submitted for publication; until it appears, cite the software:

```bibtex
@misc{perifanis2026swarmbench,
  title        = {{SwarmBench}: A Benchmark for Strategic Edge Nodes in Battery-Coupled Proportional-Share Markets},
  author       = {Perifanis, Vasilis and Pavlidis, Nikolaos},
  year         = {2026},
  howpublished = {\url{https://github.com/Indigma-Innovations/swarmbench}},
  note         = {Manuscript submitted for publication}
}
```

The repository also has a [`CITATION.cff`](https://github.com/Indigma-Innovations/swarmbench/blob/main/CITATION.cff)
file, which GitHub shows as *Cite this repository*.

When you report results, please state the SwarmBench version, the Python
version, the mode, the seeds and the agents, or simply publish the run's
`spec.json`, so that others can re-run the experiment with
`swarmbench --reproduce`.

## Acknowledgments

The arena game engine and the three baseline bots were prepared by the
[CoGNETs](https://cognets.eu/) consortium as Challenge 4 of VelesHack 2026
("Riding the Edge-to-Cloud Continuum", 6 to 8 October 2026). CoGNETs has
received funding from the European Union's Horizon Europe research and
innovation programme under grant agreement No 101135930. Nash averaging
follows Balduzzi, Tuyls, Pérolat and Graepel, *Re-evaluating evaluation*,
NeurIPS 2018.
