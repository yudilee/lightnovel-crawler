import { JobType } from '@/types';
import {
  AppstoreOutlined,
  BookOutlined,
  FileTextOutlined,
  FolderOutlined,
  PictureOutlined,
  ReadOutlined,
} from '@ant-design/icons';
import { Tag } from 'antd';

export const JobTypeTag: React.FC<{ value: JobType }> = ({ value }) => {
  function single(icon: any, name: string) {
    return <Tag icon={icon}>{name}</Tag>;
  }
  function batch(icon: any, name: string) {
    return (
      <Tag color="cyan" style={{ position: 'relative', paddingLeft: 24 }}>
        <span style={{ position: 'absolute', left: 4, top: 0 }}>{icon}</span>
        <span style={{ position: 'absolute', left: 6, top: 2 }}>{icon}</span>
        {name}
      </Tag>
    );
  }

  switch (value) {
    case JobType.NOVEL:
      return single(<BookOutlined />, 'Novel');
    case JobType.NOVEL_BATCH:
      return batch(<BookOutlined />, 'Novels');
    case JobType.FULL_NOVEL:
      return single(<ReadOutlined />, 'Full Novel');
    case JobType.FULL_NOVEL_BATCH:
      return batch(<ReadOutlined />, 'Full Novels');
    case JobType.CHAPTER:
      return single(<FileTextOutlined />, 'Chapter');
    case JobType.CHAPTER_BATCH:
      return batch(<FileTextOutlined />, 'Chapters');
    case JobType.VOLUME:
      return single(<FolderOutlined />, 'Volume');
    case JobType.VOLUME_BATCH:
      return batch(<FolderOutlined />, 'Volumes');
    case JobType.IMAGE:
      return single(<PictureOutlined />, 'Image');
    case JobType.IMAGE_BATCH:
      return batch(<PictureOutlined />, 'Images');
    case JobType.ARTIFACT:
      return single(<AppstoreOutlined />, 'Artifact');
    case JobType.ARTIFACT_BATCH:
      return batch(<AppstoreOutlined />, 'Artifacts');
    default:
      return null;
  }
};
