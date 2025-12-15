import type { Library, LibrarySummary, Paginated } from '@/types';
import { stringifyError } from '@/utils/errors';
import { PlusOutlined } from '@ant-design/icons';
import type { ButtonProps, FormInstance } from 'antd';
import {
  Button,
  Divider,
  Flex,
  Form,
  Input,
  Modal,
  Select,
  Switch,
  Typography,
  message,
} from 'antd';
import axios from 'axios';
import { useMemo, useRef, useState } from 'react';

interface FormValues {
  library_id?: string;
  name?: string;
  description?: string;
  is_public?: boolean;
}

interface Props {
  novelId: string;
  buttonText?: string;
  buttonType?: ButtonProps['type'];
  size?: ButtonProps['size'];
}

export const AddToLibraryButton: React.FC<Props> = ({
  novelId,
  buttonText = 'Add to Library',
  buttonType = 'default',
  size = 'middle',
}) => {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [libraries, setLibraries] = useState<LibrarySummary[]>([]);
  const formRef = useRef<FormInstance<FormValues>>(null);
  const [messageApi, contextHolder] = message.useMessage();

  const libraryOptions = useMemo(
    () =>
      libraries.map((item) => ({
        label: (
          <Flex align="center" justify="space-between" gap={8}>
            <span>{item.library.name}</span>
            <Typography.Text type="secondary">
              {item.novel_count} novels
            </Typography.Text>
          </Flex>
        ),
        value: item.library.id,
      })),
    [libraries]
  );

  const fetchLibraries = async () => {
    setLoading(true);
    try {
      const { data } = await axios.get<Paginated<LibrarySummary>>(
        '/api/library/my',
        { params: { limit: 100 } }
      );
      setLibraries(data.items);
    } catch (err) {
      messageApi.error(stringifyError(err));
    } finally {
      setLoading(false);
    }
  };

  const handleOpen = () => {
    setOpen(true);
    fetchLibraries();
  };

  const handleCancel = () => {
    setOpen(false);
    formRef.current?.resetFields();
  };

  const handleSubmit = async (values: FormValues) => {
    const { library_id, name, description, is_public } = values;
    if (!library_id && !name) {
      messageApi.error('Select a library or provide a name to create one.');
      return;
    }
    setSaving(true);
    try {
      let targetLibraryId = library_id;
      if (!targetLibraryId && name) {
        const { data } = await axios.post<Library>('/api/library', {
          name,
          description,
          is_public: Boolean(is_public),
        });
        targetLibraryId = data.id;
        await fetchLibraries();
      }
      if (!targetLibraryId) {
        throw new Error('No library selected');
      }
      await axios.post(`/api/library/${targetLibraryId}/novels`, {
        novel_id: novelId,
      });
      messageApi.success('Added to library');
      handleCancel();
    } catch (err) {
      messageApi.error(stringifyError(err));
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      {contextHolder}
      <Button
        icon={<PlusOutlined />}
        type={buttonType}
        size={size}
        onClick={handleOpen}
      >
        {buttonText}
      </Button>
      <Modal
        title="Add to Library"
        open={open}
        onCancel={handleCancel}
        okButtonProps={{
          loading: saving,
          htmlType: 'submit',
          form: 'add-to-library-form',
        }}
        destroyOnClose
      >
        <Form<FormValues>
          id="add-to-library-form"
          layout="vertical"
          ref={formRef}
          onFinish={handleSubmit}
          initialValues={{ is_public: false }}
        >
          <Form.Item
            label="Select an existing library"
            name="library_id"
            help="Leave empty to create a new library below"
          >
            <Select
              placeholder="Pick a library"
              loading={loading}
              allowClear
              options={libraryOptions}
            />
          </Form.Item>

          <Divider>Or create new</Divider>

          <Form.Item label="Name" name="name">
            <Input placeholder="My favorite novels" />
          </Form.Item>
          <Form.Item label="Description" name="description">
            <Input.TextArea placeholder="Optional description" rows={3} />
          </Form.Item>
          <Form.Item
            label="Make public"
            name="is_public"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
};
