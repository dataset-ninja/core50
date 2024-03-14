import csv
import glob
import os
import shutil

import supervisely as sly
from dataset_tools.convert import unpack_if_archive
from supervisely.io.fs import (
    file_exists,
    get_file_name,
    get_file_name_with_ext,
    get_file_size,
)
from tqdm import tqdm

import src.settings as s


def convert_and_upload_supervisely_project(
    api: sly.Api, workspace_id: int, project_name: str
) -> sly.ProjectInfo:
    # Possible structure for bbox case. Feel free to modify as you needs.

    images_path = "/home/alex/DATASETS/TODO/CORE/core50_350x350"
    batch_size = 30
    train_path = "/home/alex/DATASETS/TODO/CORE/core50_train.csv"
    test_path = "/home/alex/DATASETS/TODO/CORE/core50_test.csv"

    group_tag_name = "im_id"

    ds_name_to_data = {"train": train_path, "test": test_path}

    def create_ann(image_path):
        labels = []
        tags = []

        # image_np = sly.imaging.image.read(image_path)[:, :, 0]
        img_height = 350  # image_np.shape[0]
        img_wight = 350  # image_np.shape[1]

        id_data = get_file_name(image_path)[2:]
        group_id = sly.Tag(group_tag_meta, value=id_data)
        tags.append(group_id)

        session_value = int(image_path.split("/")[-3][1])
        session = sly.Tag(session_meta, value=session_value)
        tags.append(session)

        seq_value = int(image_path.split("/")[-2][1:])
        seq = sly.Tag(seq_meta, value=seq_value)
        tags.append(seq)

        obj_class = idx_to_class[seq_value]

        curr_data = name_to_data[get_file_name_with_ext(image_path)]

        curr_data = list(map(int, curr_data))

        left = curr_data[0]
        right = curr_data[2]
        top = curr_data[1]
        bottom = curr_data[3]
        if left < right and top < bottom:
            rectangle = sly.Rectangle(top=top, left=left, bottom=bottom, right=right)
            label = sly.Label(rectangle, obj_class)
            labels.append(label)

        return sly.Annotation(img_size=(img_height, img_wight), labels=labels, img_tags=tags)

    plug = sly.ObjClass("plug adapter", sly.Rectangle)
    mobile = sly.ObjClass("mobile phone", sly.Rectangle)
    scissor = sly.ObjClass("scissor", sly.Rectangle)
    bulb = sly.ObjClass("light bulb", sly.Rectangle)
    can = sly.ObjClass("can", sly.Rectangle)
    glass = sly.ObjClass("glass", sly.Rectangle)
    ball = sly.ObjClass("ball", sly.Rectangle)
    marker = sly.ObjClass("marker", sly.Rectangle)
    cup = sly.ObjClass("cup", sly.Rectangle)
    remote = sly.ObjClass("remote control", sly.Rectangle)

    classes = [plug, mobile, scissor, bulb, can, glass, ball, marker, cup, remote]

    idx_to_class = {}
    for idx, i in enumerate(range(1, 51, 5)):
        for j in range(5):
            idx_to_class[i + j] = classes[idx]

    group_tag_meta = sly.TagMeta(group_tag_name, sly.TagValueType.ANY_STRING)
    session_meta = sly.TagMeta("session", sly.TagValueType.ANY_NUMBER)
    seq_meta = sly.TagMeta("sequence", sly.TagValueType.ANY_NUMBER)

    project = api.project.create(workspace_id, project_name, change_name_if_conflict=True)
    meta = sly.ProjectMeta(obj_classes=classes, tag_metas=[group_tag_meta, session_meta, seq_meta])
    api.project.update_meta(project.id, meta.to_json())
    api.project.images_grouping(id=project.id, enable=True, tag_name=group_tag_name)

    im_name_to_path = {}
    all_images = glob.glob(images_path + "/*/*/*.png")
    for im_path in all_images:
        im_name_to_path[get_file_name_with_ext(im_path)] = im_path

    for ds_name, data_path in ds_name_to_data.items():

        dataset = api.dataset.create(project.id, ds_name, change_name_if_conflict=True)

        name_to_data = {}

        with open(data_path, "r") as file:
            csvreader = csv.reader(file)
            for idx, row in enumerate(csvreader):
                if idx > 0:
                    name_to_data[row[0].replace(".jpg", ".png")] = row[4:]

        images_names = list(name_to_data.keys())

        progress = sly.Progress("Create dataset {}".format(ds_name), len(images_names))

        for img_names_batch in sly.batched(images_names, batch_size=batch_size):
            img_pathes_batch_dual = []
            images_names_batch_dual = []
            img_pathes_batch = []
            images_names_batch = []
            for im_name in img_names_batch:
                im_path = im_name_to_path[im_name]
                depth_im_name = im_name.replace("C", "D")
                depth_im_path = im_path.replace(
                    "core50_350x350", "core50_350x350_DepthMap"
                ).replace("C_", "D_")
                if file_exists(depth_im_path):
                    images_names_batch_dual.extend([im_name, depth_im_name])
                    img_pathes_batch_dual.extend([im_path, depth_im_path])
                else:
                    images_names_batch.append(im_name)
                    img_pathes_batch.append(im_path)

            img_infos = api.image.upload_paths(
                dataset.id, images_names_batch_dual, img_pathes_batch_dual
            )
            img_ids = [im_info.id for im_info in img_infos]

            anns = []
            for i in range(0, len(img_pathes_batch_dual), 2):
                ann = create_ann(img_pathes_batch_dual[i])
                anns.extend([ann, ann])
            api.annotation.upload_anns(img_ids, anns)

            img_infos = api.image.upload_paths(dataset.id, images_names_batch, img_pathes_batch)
            img_ids = [im_info.id for im_info in img_infos]

            anns = [create_ann(image_path) for image_path in img_pathes_batch]
            api.annotation.upload_anns(img_ids, anns)

            progress.iters_done_report(len(img_names_batch))

    return project
