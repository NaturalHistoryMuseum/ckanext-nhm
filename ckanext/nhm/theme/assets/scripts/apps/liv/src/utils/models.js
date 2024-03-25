import { Model } from 'pinia-orm';

export class Resource extends Model {
  static entity = 'resources';

  static fields() {
    return {
      id: this.uid(),
      name: this.string(''),
      titleField: this.string('_id'),
      subtitleField: this.string('family'),
      imgField: this.string('associatedMedia'),
      dwc: this.boolean(false),
      packageId: this.string(''),
      packageName: this.string(''),
      data: this.attr({}),
      records: this.hasMany(Record, 'resourceId'),
    };
  }
}

export class Record extends Model {
  static entity = 'records';

  static fields() {
    return {
      id: this.uid(),
      ix: this.number(0),
      data: this.attr({}),
      manifest: this.string(''),
      images: this.hasMany(Image, 'recordId'),
      resourceId: this.string(''),
      resource: this.belongsTo(Resource, 'resourceId'),
    };
  }

  get title() {
    try {
      return this.data[this.resource.titleField];
    } catch {
      return this.id;
    }
  }

  get subtitle() {
    try {
      return this.data[this.resource.subtitleField];
    } catch {
      return null;
    }
  }

  get url() {
    if (this.data._id) {
      return `/record/${this.resourceId}/${this.data._id}`;
    }
  }

  get imageViewerUrl() {
    if (this.data._id) {
      return `/image-viewer/record/${this.resourceId}/${this.data._id}`;
    }
  }

  get displayData() {
    let data = [];
    let imgField = this.resource ? this.resource.imgField : 'associatedMedia';
    transformData(this.data, data, [imgField]);
    return data;
  }

  get dataSummary() {
    let fields = [];
    if (
      this.resource != null &&
      this.resource.id === 'bb909597-dedf-427d-8c04-4c02b3a24db3'
    ) {
      // special options for index lots
      fields = [
        'currentScientificName',
        'type',
        'phylum',
        'class',
        'order',
        'family',
        'kindOfMaterial',
      ];
    } else if (this.resource != null && this.resource.format === 'dwc') {
      fields = [
        'scientificName',
        'typeStatus',
        'phylum',
        'class',
        'order',
        'family',
        'country',
        'catalogNumber',
        'preservative',
        'collectionCode',
      ];
    } else {
      fields = Object.keys(this.data).filter((k) => k !== 'id' && k !== '_id');
    }

    if (this.resource != null) {
      fields = fields.filter((f) => {
        return (
          f !== this.resource.titleField &&
          f !== this.resource.subtitleField &&
          f !== this.resource.imgField
        );
      });
    }

    return fields.slice(0, 10).map((f) => {
      return {
        key: f,
        value: this.data[f],
      };
    });
  }
}

export class Image extends Model {
  static entity = 'images';

  static fields() {
    return {
      id: this.uid(),
      ix: this.number(0),
      url: this.string(''),
      data: this.attr({}),
      iiifData: this.attr({}),
      recordId: this.attr(null),
      record: this.belongsTo(Record, 'recordId'),
    };
  }

  get name() {
    let urlParts = this.url.split('/');
    return urlParts[urlParts.length - 1];
  }

  get thumbnail() {
    return `${this.url}/full/200,/0/default.jpg`;
  }

  get info() {
    return `${this.url}/info.json`;
  }

  get imageViewerUrl() {
    if (this.record && this.record.imageViewerUrl) {
      return `${this.record.imageViewerUrl}/${this.ix}`;
    }
  }

  get displayData() {
    let data = [];
    transformData(
      {
        ...this.data,
        maxHeight: this.iiifData.maxHeight,
        maxWidth: this.iiifData.maxWidth,
        rights: this.iiifData.rights,
      },
      data,
    );
    return data;
  }
}

function transformData(obj, outputData, exclude = [], rootKey = []) {
  return Object.entries(obj)
    .filter(
      (item) =>
        item[0] !== 'id' && item[0] !== '_id' && !exclude.includes(item[0]),
    )
    .sort((a, b) => {
      return a[0].localeCompare(b[0]);
    })
    .forEach((item) => {
      if (item[1] != null && typeof item[1] === 'object') {
        transformData(item[1], outputData, exclude, [...rootKey, item[0]]);
      } else {
        outputData.push({
          key: rootKey ? [...rootKey, item[0]].join('.') : item[0],
          value: item[1],
        });
      }
    });
}
