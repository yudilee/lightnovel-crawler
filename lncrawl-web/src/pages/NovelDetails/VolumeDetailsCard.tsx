import {
  type Chapter,
  type Job,
  type Paginated,
  type ReadHistory,
  type Volume,
} from '@/types';
import { stringifyError } from '@/utils/errors';
import { formatDate } from '@/utils/time';
import { DownloadOutlined } from '@ant-design/icons';
import {
  Button,
  Card,
  Descriptions,
  Divider,
  Flex,
  Grid,
  message,
  Pagination,
  Spin,
} from 'antd';
import axios from 'axios';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChapterListCard } from './ChapterListCard';

export const VolumeDetailsCard: React.FC<{
  volume: Volume;
  inner?: boolean;
  history?: ReadHistory;
  hideChapters?: boolean;
}> = ({ volume, inner, hideChapters, history = {} }) => {
  const navigate = useNavigate();
  const { lg } = Grid.useBreakpoint();
  const [messageApi, contextHolder] = message.useMessage();

  const [page, setPage] = useState<number>(1);
  const [total, setTotal] = useState<number>(0);
  const [perPage, setPerPage] = useState<number>(10);
  const [loading, setLoading] = useState<boolean>(true);
  const [chapters, setChapters] = useState<Chapter[]>([]);

  useEffect(() => {
    const fetchChapters = async (id: string) => {
      try {
        setLoading(true);
        const { data } = await axios.get<Paginated<Chapter>>(
          `/api/volume/${id}/chapters`,
          {
            params: {
              limit: perPage,
              offset: (page - 1) * perPage,
            },
          }
        );
        setTotal(data.total);
        setChapters(data.items);
      } catch (err) {
        messageApi.error(stringifyError(err));
        setChapters([]);
      } finally {
        setLoading(false);
      }
    };
    if (!hideChapters) {
      fetchChapters(volume.id);
    }
  }, [volume.id, hideChapters, page, perPage, messageApi]);

  const createVolumeJob = async (e: React.MouseEvent) => {
    try {
      e.stopPropagation();
      e.preventDefault();
      const result = await axios.post<Job>(`/api/job/create/fetch-volumes`, {
        volumes: [volume.id],
      });
      navigate(`/job/${result.data.id}`);
    } catch (err) {
      messageApi.error(stringifyError(err));
    }
  };

  return (
    <Card
      type={inner ? 'inner' : undefined}
      title={inner ? undefined : volume.title}
      variant={inner ? 'borderless' : undefined}
      styles={{
        body: {
          padding: 10,
        },
        title: {
          fontSize: 22,
          whiteSpace: 'wrap',
        },
      }}
    >
      {contextHolder}

      <Flex wrap vertical={!lg} align="center" justify="center" gap={10}>
        <Descriptions
          bordered
          size="small"
          layout="horizontal"
          column={lg ? 3 : 1}
          style={{ flex: 1, width: '100%' }}
          items={[
            {
              label: 'Serial',
              children: volume.serial,
            },
            {
              label: 'Chapters',
              children: volume.chapter_count ?? 0,
            },
            {
              label: 'Last Update',
              children: formatDate(volume.updated_at),
            },
          ]}
        />
        {!hideChapters && (
          <Button
            shape="round"
            type="primary"
            onClick={createVolumeJob}
            icon={<DownloadOutlined />}
            style={{ width: lg ? 100 : '100%' }}
          >
            {lg ? 'Get All' : 'Get all chapters'}
          </Button>
        )}
      </Flex>

      {hideChapters ? null : loading ? (
        <Flex align="center" justify="center">
          <Spin size="large" style={{ margin: '50px 0' }} />
        </Flex>
      ) : chapters.length > 0 ? (
        <>
          <ChapterListCard chapters={chapters} history={history} />
          <Divider size="small" />
          {(chapters.length > 0 || page > 1) && total / perPage > 1 && (
            <Pagination
              total={total}
              current={page}
              pageSize={perPage}
              onChange={(page, perPage) => {
                setPage(page);
                setPerPage(perPage);
              }}
            />
          )}
        </>
      ) : null}
    </Card>
  );
};
