import json
import unittest

from tests.helpers import load_package, ROOT


class WorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = load_package()
        cls.workflow_files = sorted((ROOT / "workflows").glob("*.json"))
        cls.workflow = json.loads(cls.workflow_files[0].read_text(encoding="utf-8"))
        cls.nodes_by_id = {node["id"]: node for node in cls.workflow["nodes"]}

    def test_only_one_formal_workflow_exists(self):
        self.assertEqual([path.name for path in self.workflow_files], ["H3GIF_Complete.json"])

    def test_workflow_uses_all_required_nodes(self):
        node_types = {node["type"] for node in self.workflow["nodes"]}
        self.assertEqual(
            node_types,
            {
                "H3GIFStoryboardDirector",
                "UNETLoader",
                "CLIPLoader",
                "VAELoader",
                "ResolutionSelector",
                "MiniMaxH3ImageConditioning",
                "BasicGuider",
                "RandomNoise",
                "KSamplerSelect",
                "ManualSigmas",
                "SamplerCustomAdvanced",
                "VAEDecode",
                "SaveImage",
                "StoryboardGridSplit",
                "StoryboardAnimation",
                "StoryboardLoopOptimizer",
                "StoryboardGIFExport",
                "MarkdownNote",
            },
        )

    def test_links_reference_existing_nodes_and_slots(self):
        node_ids = set(self.nodes_by_id)
        link_ids = set()
        for link_id, source_id, source_slot, target_id, target_slot, link_type in self.workflow["links"]:
            self.assertNotIn(link_id, link_ids)
            link_ids.add(link_id)
            self.assertIn(source_id, node_ids)
            self.assertIn(target_id, node_ids)
            source = self.nodes_by_id[source_id]
            target = self.nodes_by_id[target_id]
            self.assertLess(source_slot, len(source.get("outputs", [])))
            self.assertLess(target_slot, len(target.get("inputs", [])))
            self.assertIsInstance(link_type, str)

    def test_widget_value_counts_match_input_definitions(self):
        for node in self.workflow["nodes"]:
            node_type = node["type"]
            if node_type not in self.package.NODE_CLASS_MAPPINGS:
                continue
            node_class = self.package.NODE_CLASS_MAPPINGS[node_type]
            required = node_class.INPUT_TYPES()["required"]
            widget_names = [name for name, definition in required.items() if definition[0] != "IMAGE"]
            self.assertEqual(
                len(node["widgets_values"]),
                len(widget_names),
                msg=f"Widget count mismatch for {node_type}",
            )
            self.assertEqual(len(node["outputs"]), len(node_class.RETURN_NAMES))

    def test_director_controls_prompt_and_grid(self):
        director = next(
            node for node in self.workflow["nodes"] if node["type"] == "H3GIFStoryboardDirector"
        )
        grid = next(node for node in self.workflow["nodes"] if node["type"] == "StoryboardGridSplit")
        target_links = {item["link"] for item in grid["inputs"] if item.get("link") is not None}
        self.assertIn(director["outputs"][1]["links"][0], target_links)
        self.assertIn(director["outputs"][2]["links"][0], target_links)
        self.assertIn(director["outputs"][3]["links"][0], target_links)
        self.assertIn(director["outputs"][3]["links"][1], target_links)

    def test_h3_clip_loader_uses_minimax_type(self):
        clip_loader = next(node for node in self.workflow["nodes"] if node["type"] == "CLIPLoader")
        named = clip_loader["widgets_values_named"]
        self.assertEqual(named["type"], "minimax")
        self.assertIn("minimax_h3", named["clip_name"])

    def test_grid_frames_have_save_branch(self):
        save_nodes = [node for node in self.workflow["nodes"] if node["type"] == "SaveImage"]
        save_node = next(
            node for node in save_nodes
            if node["widgets_values"][0] == "H3GIF/frames/frame"
        )
        grid_node = next(
            node for node in self.workflow["nodes"] if node["type"] == "StoryboardGridSplit"
        )
        self.assertIn(21, grid_node["outputs"][0]["links"])
        self.assertIn(22, grid_node["outputs"][0]["links"])
        self.assertEqual(save_node["inputs"][0]["link"], 21)

    def test_workflow_contains_chinese_usage_note(self):
        note = next(node for node in self.workflow["nodes"] if node["type"] == "MarkdownNote")
        text = note["widgets_values"][0]
        self.assertIn("panel_actions", text)
        self.assertIn("gutter_pixels", text)
        self.assertIn("H3-Image", text)
        self.assertIn("GIF Export", text)

    def test_grid_node_has_detection_outputs(self):
        grid_node = next(node for node in self.workflow["nodes"] if node["type"] == "StoryboardGridSplit")
        output_names = {output["name"] for output in grid_node["outputs"]}
        self.assertIn("detection_success", output_names)
        self.assertIn("grid_info", output_names)


if __name__ == "__main__":
    unittest.main()
